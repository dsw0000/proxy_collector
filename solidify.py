#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @author: Ivo Dai
    @Contact: ivo_d@icloud.com
    @File: solidify.py
    @Time: 2018/9/25 11:12
    @Software: PyCharm
    @Environment:
    @Description: 
    @Update:
'''

from redis import StrictRedis, ConnectionPool
from json import dumps
from random import randint
import requests


class Proxy(object):
    ip = None
    port = None
    address = None
    ip_type = None
    protocol = None
    speed = None
    data_time = None
    web = None


class IpSolidify(object):

    def __init__(self, redis_url):
        """
        redis init
        :param redis_url: redis(s)://[:password]@host:port/db
        """

        self._redis_url = redis_url

        self._pool = ConnectionPool.from_url(self._redis_url)
        self._redis = StrictRedis(connection_pool=self._pool)

        self._header = "proxy_ip"
        self._invalid_time = 11 * 60

        self._proxies_list = []

        self._init_proxy_list()

    @property
    def redis(self):
        return self._redis

    def _init_proxy_list(self):
        """
        get proxy from redis
        :return:
        """
        key_words = "%s:anonymous:*:*" % (self._header,)

        keys = self._redis.keys(key_words)

        for key in keys:
            param = key.decode("utf-8").split(":")
            self._proxies_list.append("%s_%s" % (param[2], param[3].replace("_", ":"), ))

    def get_proxy(self):
        """

        :return:
        """
        proxy = {}
        if len(self._proxies_list) == 0:
            return proxy
        proxy_str = self._proxies_list[randint(0, len(self._proxies_list))].split("_")
        proxy[proxy_str[0]] = proxy_str[1]
        print(proxy)
        return proxy

    def request(self, **kwargs):
        """

        :return:
        """
        proxy = self.get_proxy()

        if len(proxy) == 0:
            html = requests.get(**kwargs).content
        else:
            html = requests.get(proxies=proxy, **kwargs).content
        return html

    def update_ip(self, proxy):
        """

        :param proxy:
        :return:
        """

        ip_info = dumps({
            "ip": proxy.ip,
            "port": proxy.port,
            "address": proxy.address,
            "ip_type": proxy.ip_type,
            "protocol": proxy.protocol,
            "speed": proxy.speed,
            "data_time": proxy.data_time,
            "web": proxy.web,
        })

        try:
            ip_key = "%s_%s" % (proxy.ip, proxy.port)
            ip_type = proxy.ip_type
        except KeyError:
            raise KeyError

        key = "%s:%s:%s:%s" % (self._header, ip_type, proxy.protocol, ip_key)

        # if self._redis.exists(key):
        #     self._redis.expire(key, self._invalid_time)
        # else:
        self._redis.set(name=key, value=ip_info, ex=self._invalid_time)
