# abs()
num_one = -10
print(abs(num_one))

# all
# 如果iterable中的所有元素都为真值
all([1, 2, 3, 4, 5])


# 等价于
def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True


