from datetime import datetime

dt1 = datetime(year=2025, month=2, day=1, hour=1, minute=1, second=2)
dt2 = datetime(year=2025, month=2, day=1, hour=1, minute=1, second=0)
total_second = (dt2 - dt1).total_seconds()
total_second

dt2 = datetime(year=2025, month=2, day=2)

dt2 < dt1

import time


def test_while(n):
    while True:
        if n < 10:
            n += 1
            time.sleep(2)
        else:
            return n

test_while(5)

def test_tuple(n):
    try:
        if n > 1:
            return 1, True, "ok"
        raise Exception("不满足")
    except Exception as e:
        return 0, False, str(e)

a, b, c = test_tuple(1)

a

b

class Person:
    def __init__(self):
        a = 1
        b = 2
        

b = Person()
if b:
    print(11)
else:
    print(22)

d1 = {1: "1", 2: "2"}

list(d1)
