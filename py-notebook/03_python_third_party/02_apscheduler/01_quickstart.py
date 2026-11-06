# ## 基本概念
#
# APScheduler 有如下四种组件：
#
# **triggers 触发器**:包含具体的角度逻辑。每个 job 都会有自己的触发器，由它来决定下一个要运行的 job 。在触发器被初始化配置之前，它们都是完全无状态（stateless）的。
#
# **job stores 作业存储**:存放被调度的 job 。默认的作业存储只是简单地将作业存储在内存中，但也可以存储到各种数据库中。当一个 job 保存到一个持久化地作业存储中时，其数据必须要被序列化（serialized），当它们被加载回来时再执行反序列化（deserialized）。非默认的作业存储不会将作业数据保存到内存中，相反，内存会作为后端存储介质在保存、加载、更新和搜索 job 过程中的中间人。作业存储不会在调度器（scheduler）之间共享。
#
# **executors 执行器**:负责处理运行中的作业。通常它们都是负责将 job 中指定的可调用的部分提交到线程或进程池。当 job 完成后，执行器会通知（notifies）调度器，由调度器随后发出（emits）一个恰当的事件（event）。
#
# **schedulers 调度器**: 调度器负责将以上的东西结合在一起。一般情况下，你的应用程序只会有一个调度器在运行。应用程序的开发者通常不用直接面对 trigger ， job stores 以及 executor ，相反，调度器会提供合适的接口让开发者去管理它们 —— 通过调度程序来配置 job stores 和 executor 来实现诸如添加、修该和删除 job 。

# ## 调度器选择
# scheduler 的选择取决于你程序的运行环境以及你想用 APScheduler 完成什么任务。这里有一份快速决定 scheduler 的指南：
#
# BlockingScheduler: 如果调度器是你程序中唯一要运行的东西，请选择它
#
# BackgroundScheduler: 如果你想你的调度器可以在你的应用程序后台静默运行，同时也不打算使用以下任何 Python 框架，请选择它
#
# AsyncIOScheduler: 如果你的程序使用了 asyncio 库，请使用这个调度器
#
# GeventScheduler: 如果你的程序使用了 gevent 库，请使用这个调度器
#
# TornadoScheduler: 如果你打算构建一个 Tornado 程序，请使用这个调度器
#
# TwistedScheduler: 如果你打算构建一个 Twisted 程序，请使用这个调度器
#
# QtScheduler: 如果你打算构建一个 Qt 程序，请使用这个调度器

# ## 储存器选择
# **MemoryJobStore**: 总是再应用程序开始的时候重新创建你的作业，那么你适合用默认的选项（MemoryJobStore）。
#
# **SQLAlchemyJobStore**: 需要持久化你的作业以面对 scheduler 重启或者应用程序崩溃的情况，那么你的选择通常需要考虑你在程序运行环境中所使用的工具。当然，如果你可以自由选择的话，我们建议使用 SQLAlchemyJobStore 配合 PostgreSQL 作为后端存储，因为这个组合提供了强大的数据完整性的保障。

# ## 触发器选择
# date 在某个确定的时间点运行你的 job （只运行一次）
#
# interval 在固定的时间间隔周期性地运行你的 job
#
# cron 在一天的某些固定时间点周期性地运行你的 job

# 使用默认的 job store 以及默认的 executor ，在你的应用程序中运行一个 BackgroundScheduler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
# 在这里可以初始化应用程序的剩余部分，当然也可以在初始化 scheduler 之前完成

"""
下面是一个更加复杂而具体的例子：你有两个 job store 以及两个 executor ，同时要求调整新作业的默认值以设置不同的时区。以下的三段代码片段都是等价的。你会得到：

一个叫 mongo 的 MongoDBJobStore
一个叫 default 的 SQLAlchemyJobStore （使用 SQLite）
一个叫 default 的 ThreadPoolExecutor，使用 20 个工作线程
一个叫做 processpool 的 ProcessPoolExecutor，使用 5 个工作进程
UTC 是调度器的时区
新 job 默认关闭聚合（coalescing）功能
每个新 job 默认限制最大实例数为 3
"""
# Method 1
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

jobstores = {
    'mongo': MongoDBJobStore(),
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


# Method 2
from apscheduler.schedulers.background import BackgroundScheduler

# 前缀 "apscheduler." 是硬编码的
scheduler = BackgroundScheduler({
    'apscheduler.jobstores.mongo': {
         'type': 'mongodb'
    },
    'apscheduler.jobstores.default': {
        'type': 'sqlalchemy',
        'url': 'sqlite:///jobs.sqlite'
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '20'
    },
    'apscheduler.executors.processpool': {
        'type': 'processpool',
        'max_workers': '5'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
    'apscheduler.timezone': 'UTC',
})

# Method 3
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor


jobstores = {
    'mongo': {'type': 'mongodb'},
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler()

# do something else here, maybe add jobs etc.

scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


# ## trigger详解
# ### date trigger
# ### interval trigger
# ### cron trigger

# ## date trigger
# date 是最基本的一种调度，job 只会执行一次，它表示特定的时间点触发

from datetime import date, datetime
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler

def my_job(text):
    print(text)

# job 将在 2009 年 11 月 6 日 16:30:05 运行
sched.add_job(my_job, "date", run_date=datetime(2009, 11, 6, 16, 30, 5), args=["text"])
# 另一种写法
sched.add_job(my_job, "date", run_date="2009-11-06 16:30:05", args=["text"])

sched.start()

# ## interval trigger
# interval 表示周期性触发触发

from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler


def job_function():
    print("Hello World")

sched = BlockingScheduler()

# job_function 每两个小时执行一次，同时添加了 jitter 可以增加随机性
# 防止如多个服务器在同一时间运行某个 job 时会非常有用
sched.add_job(job_function, 'interval', hours=2, jitter=120, start_date="2010-10-10 09:30:00", end_date="2014-06-15 11:00:00")

sched.start()

# ## cron trigger
# cron 提供了和 Linux crontab 格式兼容的触发器，是功能最为强大的触发器，其参数如下所示：
#
# year(int|str) - 4 位年份
# month(int|str) - 2 位月份(1-12)
# day(int|str) - 一个月内的第几天(1-31)
# week(int|str) - ISO 礼拜数(1-53)
# day_of_week(int|str) - 一周内的第几天(0-6 或者 mon, tue, wed, thu, fri, sat, sun)
# hour(int|str) - 小时(0-23)
# minute(int|str) - 分钟(0-59)
# second(int|str) - 秒(0-59)
# start_date(datetime|str) - 最早可能触发的时间(date/time)，含该时间点
# end_date(datetime|str) - 最后可能触发的时间(date/time)，含该时间点
# timezone(datetime.tzinfo|str) - 计算 date/time 时所指定的时区（默认为 scheduler 的时区）
# jitter(int|None) - 最多提前或延后执行 job 的 偏振 秒数
# 一周的开始时间总是周一！
#
# 对于 cron trigger 来说，它的强大在于可以在每个参数字段上指定各种不同的表达式来确定下一个执行时间，类似于 Unix 的 cron 程序。但和 crontab 表达式不同的是，你可以忽略不需要的字段，其行为如下 大于你显式指定的最小参数字段的参数默认都为 * ，而小于的则默认为最小值（week 和 day_of_week 除外）。 这是 ApScheduler 2.0 修正后的默认行为，在此之前忽略的字段始终默认为 * 。如 day=1, minute=20 等同于 year="*", month="*", day=1, week="*", day_of_week="*", day_of_week="*", hour="*", minute=20, second=0 。

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler


def job_function():
    print("Hello World")

sched = BlockingScheduler()

# job_function 会在 6、7、8、11、12 月的第三个周五的 00:00, 01:00, 02:00 以及 03:00 执行
sched.add_job(job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')

# 可以使用装饰器模式

def some_decorated_task():
    print("I am printed at 00:00:00 on the last Sunday of every month!")

# 或者直接使用 crontab 表达式
sched.add_job(job_function, CronTrigger.from_crontab('0 0 1-15 may-aug *'))

# ### 启动shceduler
# 调用scheduler上的start方法

# ### 添加job
# 1. 调用add_job()方法
# 2. 使用scheduled_job()装饰一个函数

# ### 移除job
# 1. 通过 job 的 ID 以及 job store 的别名来调用 remove_job() 方法
# 2. 对你在 add_job() 中得到的 job 实例调用 remove() 方法

# 其他详见: https://sinhub.cn/2018/11/apscheduler-user-guide/
