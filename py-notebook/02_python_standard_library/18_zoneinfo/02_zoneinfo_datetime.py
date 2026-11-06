from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones



# datetime分为感知型和简单型
# 感知型就是带时区的datetime
# 简单型就是不带时区的datetime

format = "%Y-%m-%d %H:%M:%S"

datetime.now().strftime(format)

datetime.now(tz=ZoneInfo("America/New_York")).strftime(format)

str1 = "2025-03-19 05:34:26"

dt1 = datetime.strptime(str1, format)
print(dt1.tzinfo)
print(dt1.tzname())
print(dt1.dst())

dt2 = datetime.strptime(str1, format).replace(tzinfo=ZoneInfo("America/New_York"))
print(dt2.tzinfo)
print(dt2.tzname())
print(dt2.dst())
print(dt2.utcoffset())
print(dt2)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zoneinfo
from datetime import datetime


class TimeZone:
    def __init__(self, tz: str = 'Asia/Singapore'):
        self.tz_info = zoneinfo.ZoneInfo(tz)

    def now(self) -> datetime:
        """
        获取时区时间

        :return:
        """
        return datetime.now(self.tz_info)

    def f_datetime(self, dt: datetime) -> datetime:
        """
        datetime 时间转时区时间

        :param dt:
        :return:
        """
        return dt.strf
        return dt.astimezone(self.tz_info)

    def f_str(self, date_str: str, format_str: str = 'Asia/Singapore') -> datetime:
        """
        时间字符串转时区时间

        :param date_str:
        :param format_str:
        :return:
        """
        return datetime.strptime(date_str, format_str).replace(tzinfo=self.tz_info)


timezone = TimeZone()

d1 = {"123": "123"}
print(d1.get("123"))

print(d1.get("124"))

print(d1["133"])


