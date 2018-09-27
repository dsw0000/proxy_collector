#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @author: Ivo Dai
    @Contact: ivo_d@icloud.com
    @File: collect_schedule.py
    @Time: 2018/9/25 17:42
    @Software: PyCharm
    @Environment:
    @Description: 
    @Update:
'''

import schedule
import time

from proxy_collector import main



if __name__ == "__main__":

    period = 10

    schedule.every(period).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
