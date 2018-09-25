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

    @property
    def redis(self):
        return self._redis

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

        key = "%s:%s:%s" % (self._header, ip_type, ip_key)

        if self._redis.exists(key):
            self._redis.expire(key, self._invalid_time)
        else:
            self._redis.set(name=key, value=ip_info, ex=self._invalid_time)

