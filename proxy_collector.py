#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @author: Ivo Dai
    @Contact: ivo_d@icloud.com
    @File: sp_test.py
    @Time: 2018/9/23 15:26
    @Software: PyCharm
    @Environment:
    @Description: 
    @Update:
'''

from bs4 import BeautifulSoup
import requests
import time
from solidify import Proxy, IpSolidify
from threading import Thread
from queue import Queue
from re import findall


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 \
    Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

proxies = {
    "http": "http://114.112.70.150:57871"  # 代理ip
}

PAGE = 5

redis_url = "redis://:Dsw871127@shao5.net:30001/1"


def get_proxies_xici():
    url_header = 'http://www.xicidaili.com/%s/%d'

    ip_result = []

    web = "xici"
    type_list = {
        "nn": "anonymous",
        "nt": "pellucid"
    }

    for item in type_list:
        for page in range(1, PAGE + 1):
            url = url_header % (item, page)
            html = requests.get(url=url, headers=headers).content
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find_all('tr')

            for ip in ip_list:
                ip_pa = ip.find_all('td')
                if ip_pa:
                    proxy = Proxy()
                    proxy.web = web

                    if ip_pa[0].find('img'):
                        contry = ip_pa[0].find('img').attrs['alt']
                    else:
                        contry = None

                    ip = ip_pa[1].get_text()
                    proxy.ip = ip

                    port = ip_pa[2].get_text()
                    proxy.port = port

                    if ip_pa[3].find('a'):
                        address = ip_pa[3].find('a').get_text()
                    else:
                        address = None
                    proxy.address = address

                    ip_type = ip_pa[4].get_text()
                    proxy.ip_type = type_list[item]
                    # print(ip_type)

                    protocol = ip_pa[5].get_text()
                    proxy.protocol = protocol.lower()

                    speed = float(ip_pa[6].find(class_='bar').attrs['title'].replace(u'秒', ''))
                    proxy.speed = speed

                    connect_time = float(ip_pa[7].find(class_='bar').attrs['title'].replace(u'秒', ''))

                    invalid_day = ip_pa[8].get_text().replace(u'天', '')

                    data_time = ip_pa[9].get_text() + ':00'
                    proxy.data_time = data_time

                    ip_result.append(proxy)
    return ip_result


def get_proxies_kuai():
    """
    https://www.kuaidaili.com/
    :return:
    """
    url_header = 'https://www.kuaidaili.com/free/'
    type_list = {
        "inha/": "anonymous",
        "intr/": "pellucid"
    }
    web = "kuai"

    ip_result = []

    for item in type_list:
        for page in range(1, PAGE + 1):
            if page > 1:
                url = url_header + item + str(page)
            else:
                url = url_header + item

            html = requests.get(url=url, headers=headers).content
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find_all('tr')
            if not len(ip_list):
                print("error web.")
            ip_list.pop(0)

            for ip in ip_list:
                proxy = Proxy()
                proxy.web = web

                ip_pa = ip.find_all('td')
                # print(ip_pa)

                ip = ip_pa[0].get_text()
                proxy.ip = ip

                port = ip_pa[1].get_text()
                proxy.port = port

                ip_type = ip_pa[2].get_text()[1:]
                proxy.ip_type = type_list[item]
                # print(proxy.ip_type)

                protocol = ip_pa[3].get_text()
                proxy.protocol = protocol.lower()

                address = ip_pa[4].get_text()
                proxy.address = address

                speed = ip_pa[5].get_text()
                proxy.speed = speed[:-1]

                data_time = ip_pa[6].get_text()
                proxy.data_time = data_time

                ip_result.append(proxy)

            time.sleep(0.9)

    return ip_result


def get_proxies_66():
    """
    http://www.66ip.cn/
    :return:
    """
    url = "http://www.66ip.cn/nmtq.php?getnum=300&isp=0&anonymoustype=%s&start=&ports=&export=&ipaddress=&area=0&\
    proxytype=%d&api=66ip"
    protocols = {"http": 0, "https": 1}
    type_list = {"1": "anonymous", "4": "pellucid"}
    web = "66"

    proxy_list = []
    for ip_type in type_list:
        for protocol in protocols:
            while True:
                html = requests.get(url % (ip_type, protocols[protocol]), headers=headers).content
                soup = BeautifulSoup(html, 'lxml')
                if soup:
                    break
                time.sleep(1)
            ip_list = soup.find('p')
            ip_list = findall(r'[1-9]\d*.[1-9]\d*.[1-9]\d*.[1-9]\d*\:[1-9]\d*', ip_list.text)

            for ip in ip_list:
                proxy = Proxy()
                proxy.web = web
                proxy.ip = ip.split(':')[0]
                proxy.port = ip.split(':')[1]
                proxy.protocol = protocol
                proxy.ip_type = type_list[ip_type]
                proxy_list.append(proxy)
    return proxy_list


def verify_one_proxy(old_queue, new_queue, num):
    while 1:
        proxy = old_queue.get()
        if proxy == 0:
            break
        protocol = proxy.protocol
        url = "%s://%s:%s" % (proxy.protocol, proxy.ip, proxy.port)
        proxies = {protocol: url}

        try:
            start_time = time.time()
            if requests.get('http://www.baidu.com', proxies=proxies, timeout=3).status_code == 200:
                print('success %s' % url)
                proxy.speed = round(time.time() - start_time, 1)
                new_queue.put(proxy)
        except Exception:
            print('fail %s' % url)
    print("exit process %d." % num)


def main():
    proxies_list = []
    proxies_list.extend(get_proxies_xici())
    proxies_list.extend(get_proxies_kuai())
    proxies_list.extend(get_proxies_66())

    # 没验证的代理
    old_queue = Queue()
    # 验证后的代理
    new_queue = Queue()

    print('verify proxy........')
    works = []
    process_num = 30
    for num in range(process_num):
        works.append(Thread(target=verify_one_proxy, args=(old_queue, new_queue, num)))
    for work in works:
        work.start()
    for proxy in proxies_list:
        old_queue.put(proxy)
    for _ in works:
        old_queue.put(0)
    for work in works:
        work.join()
    proxies_list = []
    while 1:
        if new_queue.empty():
            break
        proxies_list.append(new_queue.get(timeout=1))

    print('verify_proxies done!')
    print(len(proxies_list))

    rs = IpSolidify(redis_url)
    for proxy in proxies_list:
        rs.update_ip(proxy)

    print("save success.")


if __name__ == "__main__":

    main()
