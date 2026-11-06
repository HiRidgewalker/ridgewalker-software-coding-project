# # 标准库 datetime

import datetime


# 常量
datetime.MINYEAR, datetime.MAXYEAR

# # timedelta模块

from datetime import timedelta

year = timedelta(days=365)
another_year = timedelta(weeks=40, days=84, hours=23, minutes=50, seconds=600)
year == another_year, year.total_seconds()

from datetime import timedelta

year = timedelta(days=365)
ten_years = 10 * year
print(ten_years)

datetime.timedelta(days=3650)
print(ten_years.days // 365)

nine_years = ten_years - year
print(nine_years)

datetime.timedelta(days=3285)
three_years = nine_years // 3
print(three_years, three_years.days // 365)


# # date

from datetime import date

# 获取今日日期
date.today()

# date类属性
date.min, date.max, date.resolution

# 实例属性
date_ = date(2024, 12, 17)
date_.year, date_.month, date_.day

# 支持运算
date1 = date(2024, 12, 17)
date2 = date1 + timedelta(days=20)
date2.strftime("%Y-%m-%d")

# date的计算
date_two = date(2024, 12, 15)
date_three = date(2024, 12, 17)
# date_two > date_three
date_two + timedelta(days=2) == date_three

# # datetime

from datetime import datetime

datetime.now()

datetime.now().weekday()

datetime.now().isoweekday()


# # time模块

from datetime import time
import random

# 获取一个iso格式的时间字符串 格式化成 datetime.time类
iso_time = "08:57:59"
duration_time = time.fromisoformat(iso_time)


duration_time

time.isoformat(duration_time, timespec='seconds')

duration_time.hour

duration_time.minute

duration_time.second

time_one = time(hour=8, minute=57, second=55)
time_two = time(hour=13, minute=57, second=55)

print(time_one)

print(time_two)

print(type(time_two - time_one))

is_true = time_two > time_one

is_true

print(time.max)

print(time.min)

print(time.max.hour)

print(time.max.minute)

print(time.max.second)

iso_time = "08:00:00"
duration_time = time.fromisoformat(iso_time)
remain_hour = time.max.hour - duration_time.hour
remain_minute = time.max.minute - duration_time.minute
remain_second = time.max.minute - duration_time.second

start_hour = random.randint(0, remain_hour)
start_minute = random.randint(0, remain_minute)
start_second = random.randint(0, remain_second)

start_run_task_time = time(hour=start_hour, minute=start_minute, second=start_second)
start_run_task_time.isoformat(timespec="seconds")

random.randint(0, 1)

iso_duration_time = "08:00:00"
iso_start_time = "12:39:38"
start_execution_time = time.fromisoformat(iso_start_time)
duration_execution_time = time.fromisoformat(iso_duration_time)
end_execution_time = time(
    hour=start_execution_time.hour + duration_execution_time.hour,
    minute=start_execution_time.minute + duration_execution_time.minute,
    second=start_execution_time.second + duration_execution_time.second
)

end_execution_time.isoformat(timespec="seconds")



from datetime import datetime, time

datetime.now()

print(type(datetime.now().time()))

start_execution_time = "10:00:00"
end_execution_time = "12:00:00"
now_time = datetime.now().time()
if (time.fromisoformat(start_execution_time) < now_time) and (now_time < time.fromisoformat(end_execution_time)):
    print(True)
else:
    print(False)

from datetime import timedelta

iso_duration_time = "08:00:00"
duration_time = time.fromisoformat(iso_duration_time)
duration_time_total_seconds = timedelta(hours=duration_time.hour, minutes=duration_time.minute,
                                        seconds=duration_time.second).total_seconds()
print(type(duration_time_total_seconds))

print(60 * 60 * 8)

2.0 / 2

2 / 1.0

2 / 2

print(int(2) / int(2))

datetime.today()

from datetime import date

date.today()

time = datetime.now().time()
day = datetime.now().date()

datetime_ = datetime.combine(date.today(), time)

datetime_

a = 0
if a:
    print(True)
else:
    print(False)

datetime.now().date() == datetime.strptime(date_, "%Y-%m-%d").date()
