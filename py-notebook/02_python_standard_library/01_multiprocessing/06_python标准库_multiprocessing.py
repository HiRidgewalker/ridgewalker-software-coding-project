# # python标准库 multiprocessing

# Process 类
# 在 multiprocessing 中，通过创建一个 Process 对象然后调用它的 start() 方法来生成进程。 Process 和 threading.Thread   PI 相同。 一个简单的多进程程序示例是:

from multiprocessing import Process

def f(name):
    print('hello', name)

if __name__ == '__main__':
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()


