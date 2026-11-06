#!/usr/bin/env python
# _*_ coding: utf-8 _*_

print("hello world")

# 使用装饰器安排工作
from schedule import every, repeat, run_pending
import time


@repeat(every(10).minutes)
def job():
    print("I am a scheduled job")


while True:
    run_pending()
    time.sleep(1)
