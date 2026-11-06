from numbers import Number

class Animal:
    pass

class Dog(Animal):
    pass

a1 = Animal()
d1 = Dog()
print("############ type ############")
print(type(a1) is Animal)
print(type(d1) is Dog)
print(type(d1) is Animal)
print("########### isinstance ###########")
print(isinstance(a1, Animal))
print(isinstance(d1, Dog))
print(isinstance(d1, Animal))



# type和isinstance的区别:
# type: 获取对象的确切类型或验证精确类型
# isinstance: 检查对象是否是某类或其子类的实例

