# unittest 快速学习

这是一份面向初学者的 `unittest` 快速入门文档，目标是让你尽快掌握三件事：

- `unittest` 怎么写、怎么运行。
- `unittest` 常用测试功能有哪些。
- 如何通过几个小案例快速上手，并能直接运行代码。

`unittest` 是 Python 标准库自带的测试框架，不需要额外安装。  
只要你的环境里有 Python 3，就可以直接使用。

## 1. unittest 是什么

`unittest` 是 Python 官方标准库中的单元测试框架，适合做下面这些事：

- 为函数、类、模块编写自动化测试。
- 在改代码后快速验证功能是否被破坏。
- 通过断言检查实际结果和预期结果是否一致。
- 把测试组织成测试类和测试套件，方便统一执行。

它的特点是：

- Python 自带，无需安装。
- 结构清晰，适合学习测试基础。
- 支持测试发现、夹具、跳过、参数化风格循环、mock 等常见能力。

## 2. unittest 怎么运行测试

最常见的运行方式有三种。

### 方式 1：直接运行某个测试文件

```bash
python3 test_calculator.py
```

前提是测试文件里有：

```python
if __name__ == "__main__":
    unittest.main()
```

### 方式 2：以模块方式运行

```bash
python3 -m unittest test_calculator.py
```

也可以运行某个测试类或某个测试方法：

```bash
python3 -m unittest test_calculator.TestCalculator
python3 -m unittest test_calculator.TestCalculator.test_add
```

### 方式 3：自动发现测试

这是项目里最常见的方式。

```bash
python3 -m unittest discover -s tests -v
```

参数说明：

- `discover`：自动发现测试文件。
- `-s tests`：从 `tests` 目录开始找。
- `-v`：输出更详细的执行信息。

## 3. unittest 的基本写法

`unittest` 最常见的结构如下：

```python
import unittest


def add(a, b):
    return a + b


class TestAdd(unittest.TestCase):
    def test_add_two_numbers(self):
        result = add(1, 2)
        self.assertEqual(result, 3)


if __name__ == "__main__":
    unittest.main()
```

这里有几个关键点：

- 测试类通常继承 `unittest.TestCase`。
- 测试方法名通常以 `test_` 开头。
- 使用 `self.assertEqual(...)` 这样的断言来验证结果。
- `unittest.main()` 用来在直接运行文件时启动测试。

## 4. 常用断言

写测试时最常用的是断言。断言的作用是检查“实际结果是否符合预期”。

常见断言如下：

| 断言 | 用途 |
| --- | --- |
| `assertEqual(a, b)` | 判断 `a == b` |
| `assertNotEqual(a, b)` | 判断 `a != b` |
| `assertTrue(x)` | 判断 `x` 为真 |
| `assertFalse(x)` | 判断 `x` 为假 |
| `assertIs(a, b)` | 判断两者是同一个对象 |
| `assertIsNone(x)` | 判断值是否为 `None` |
| `assertIn(a, b)` | 判断 `a` 是否在 `b` 中 |
| `assertNotIn(a, b)` | 判断 `a` 是否不在 `b` 中 |
| `assertRaises(exc)` | 判断代码是否抛出指定异常 |
| `assertAlmostEqual(a, b)` | 判断浮点数是否近似相等 |

示例：

```python
import unittest


class TestAssertions(unittest.TestCase):
    def test_common_assertions(self):
        self.assertEqual(1 + 1, 2)
        self.assertNotEqual(1 + 1, 3)
        self.assertTrue(10 > 1)
        self.assertFalse(1 > 10)
        self.assertIsNone(None)
        self.assertIn("py", "python")
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)


if __name__ == "__main__":
    unittest.main()
```

## 5. 常用测试功能有哪些

下面这些能力，是实际开发里最常见、最值得优先掌握的。

### 5.1 `setUp` 和 `tearDown`

用于在每个测试方法执行前后做准备和清理。

- `setUp`：每个测试方法执行前调用一次。
- `tearDown`：每个测试方法执行后调用一次。

适合场景：

- 创建测试对象。
- 初始化临时数据。
- 清理测试现场。

### 5.2 `setUpClass` 和 `tearDownClass`

用于在整个测试类执行前后做一次性准备和清理。

- `setUpClass`：整个类开始前执行一次。
- `tearDownClass`：整个类结束后执行一次。

适合场景：

- 建立数据库连接。
- 初始化共享资源。
- 启动和关闭一次性测试依赖。

### 5.3 `assertRaises`

用于测试异常分支。

适合场景：

- 非法输入。
- 参数校验失败。
- 业务规则不满足时报错。

### 5.4 `subTest`

可以让你在一个测试方法里跑多组输入，并分别报告结果。

适合场景：

- 一组类似用例的批量验证。
- 减少重复测试代码。

### 5.5 `skip` / `skipIf` / `skipUnless`

用于跳过某些测试。

适合场景：

- 某功能暂时未完成。
- 只在特定操作系统运行。
- 依赖环境不满足。

### 5.6 `expectedFailure`

用于标记“当前预期会失败”的测试。

适合场景：

- 先写好测试，等待缺陷修复。
- 临时记录已知问题。

### 5.7 `mock`

来自标准库 `unittest.mock`，用来模拟依赖对象。

适合场景：

- 不希望真的访问数据库。
- 不希望真的发 HTTP 请求。
- 只想测试当前函数逻辑，不想连带测外部系统。

## 6. 小案例 1：测试普通函数

这个案例演示最基础的函数测试。

目录结构可以如下：

```text
case1/
├── calculator.py
└── test_calculator.py
```

### `calculator.py`

```python
def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("b cannot be zero")
    return a / b
```

### `test_calculator.py`

```python
import unittest

from calculator import add, divide


class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)


if __name__ == "__main__":
    unittest.main()
```

运行方式：

```bash
python3 test_calculator.py
```

你会学到：

- 怎么写最基本的测试类。
- 怎么验证正常结果。
- 怎么验证异常分支。

## 7. 小案例 2：使用 setUp 和 tearDown

这个案例演示如何在每个测试前准备测试对象。

### `shopping_cart.py`

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name):
        self.items.append(name)

    def remove_item(self, name):
        self.items.remove(name)

    def count(self):
        return len(self.items)
```

### `test_shopping_cart.py`

```python
import unittest

from shopping_cart import ShoppingCart


class TestShoppingCart(unittest.TestCase):
    def setUp(self):
        # 每个测试方法开始前，都会创建一个全新的购物车对象。
        # 这样每个测试之间互不影响，避免脏数据。
        self.cart = ShoppingCart()

    def tearDown(self):
        # 这个案例里不做复杂清理，只是演示这个钩子的存在。
        self.cart = None

    def test_add_item(self):
        self.cart.add_item("apple")
        self.assertEqual(self.cart.count(), 1)

    def test_remove_item(self):
        self.cart.add_item("apple")
        self.cart.remove_item("apple")
        self.assertEqual(self.cart.count(), 0)


if __name__ == "__main__":
    unittest.main()
```

你会学到：

- 为什么测试之间要隔离。
- `setUp` 为什么很常用。
- 如何避免多个测试共享状态。

## 8. 小案例 3：使用 subTest 跑多组数据

这个案例适合学习“类似参数化测试”的写法。

### `test_even_number.py`

```python
import unittest


def is_even(number):
    return number % 2 == 0


class TestIsEven(unittest.TestCase):
    def test_is_even(self):
        cases = [
            (2, True),
            (4, True),
            (5, False),
            (9, False),
        ]

        for number, expected in cases:
            with self.subTest(number=number, expected=expected):
                self.assertEqual(is_even(number), expected)


if __name__ == "__main__":
    unittest.main()
```

你会学到：

- 如何在一个测试方法中覆盖多组样例。
- 失败时如何更容易定位是哪组输入有问题。

## 9. 小案例 4：跳过测试和预期失败

这个案例演示一些在项目中很常见的测试管理功能。

### `test_control_features.py`

```python
import os
import unittest


class TestControlFeatures(unittest.TestCase):
    @unittest.skip("暂时跳过这个测试，用于演示 skip")
    def test_skip_example(self):
        self.assertEqual(1, 2)

    @unittest.skipUnless(os.name == "posix", "只在 POSIX 系统运行")
    def test_only_on_posix(self):
        self.assertTrue(True)

    @unittest.expectedFailure
    def test_expected_failure(self):
        # 这个测试当前故意失败，用来演示 expectedFailure。
        self.assertEqual(1 + 1, 3)


if __name__ == "__main__":
    unittest.main()
```

你会学到：

- 怎么暂时跳过某个测试。
- 怎么按环境条件跳过测试。
- 怎么标记“已知会失败”的用例。

## 10. 小案例 5：使用 mock 模拟外部依赖

这是实际开发中非常重要的能力。

假设有一个函数，会依赖另一个对象提供汇率：

### `payment.py`

```python
def convert_price(exchange_service, amount, from_currency, to_currency):
    rate = exchange_service.get_rate(from_currency, to_currency)
    return amount * rate
```

### `test_payment.py`

```python
import unittest
from unittest.mock import Mock

from payment import convert_price


class TestPayment(unittest.TestCase):
    def test_convert_price(self):
        # Mock 用来模拟一个“假的汇率服务”。
        # 这样测试时就不需要真的访问网络或数据库。
        fake_exchange_service = Mock()
        fake_exchange_service.get_rate.return_value = 7.0

        result = convert_price(fake_exchange_service, 10, "USD", "CNY")

        self.assertEqual(result, 70.0)
        fake_exchange_service.get_rate.assert_called_once_with("USD", "CNY")


if __name__ == "__main__":
    unittest.main()
```

你会学到：

- 如何隔离外部依赖。
- 如何验证 mock 是否被正确调用。
- 为什么 mock 对单元测试很重要。

## 11. 一个完整的可运行练习

如果你想快速练手，建议先跑下面这个最小练习。它只包含两个文件，但覆盖了 `assertEqual`、`assertRaises`、`setUp` 三个最核心知识点。

目录结构：

```text
quick-demo/
├── bank_account.py
└── test_bank_account.py
```

### `bank_account.py`

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdraw amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient balance")
        self.balance -= amount
```

### `test_bank_account.py`

```python
import unittest

from bank_account import BankAccount


class TestBankAccount(unittest.TestCase):
    def setUp(self):
        # 每个测试开始前都初始化一个新账户，
        # 确保不同测试互不影响。
        self.account = BankAccount("Alice", 100)

    def test_deposit(self):
        self.account.deposit(50)
        self.assertEqual(self.account.balance, 150)

    def test_withdraw(self):
        self.account.withdraw(40)
        self.assertEqual(self.account.balance, 60)

    def test_withdraw_too_much(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(200)

    def test_deposit_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(0)


if __name__ == "__main__":
    unittest.main()
```

运行命令：

```bash
python3 test_bank_account.py
```

或者：

```bash
python3 -m unittest test_bank_account.py -v
```

## 12. 在真实项目中怎么组织 unittest

比较常见的目录结构如下：

```text
project/
├── app/
│   ├── __init__.py
│   └── calculator.py
└── tests/
    ├── __init__.py
    └── test_calculator.py
```

测试文件命名建议：

- `test_xxx.py`
- 测试类名可以写成 `TestXxx`
- 测试方法名统一以 `test_` 开头

这样可以更方便地被 `unittest discover` 自动发现。

## 13. 学习顺序建议

如果你是初学者，建议按这个顺序学：

1. 先学最基础的测试类和断言。
2. 再学 `assertRaises`，补上异常测试。
3. 再学 `setUp` / `tearDown`。
4. 然后学 `subTest`，批量跑测试样例。
5. 最后学习 `mock`，进入更真实的项目测试。

这个顺序比较稳，不容易一开始就被高级功能绕进去。

## 14. 常见问题

### 为什么测试方法必须以 `test_` 开头

因为 `unittest` 默认会按命名规则发现测试方法。  
如果不以 `test_` 开头，通常不会被自动识别。

### 为什么推荐测试之间互相独立

因为测试互相依赖会导致结果不稳定。  
一个测试修改的状态，可能影响另一个测试，最后就会出现偶发失败。

### unittest 和 pytest 有什么关系

- `unittest` 是 Python 标准库自带框架。
- `pytest` 是第三方框架，写法通常更灵活。

如果你是初学者，先学 `unittest` 很合适，因为它能帮助你建立测试的基本概念。  
之后再学 `pytest` 会更轻松。

## 15. 总结

学习 `unittest`，最重要的不是背 API，而是先掌握这几个核心动作：

- 写一个 `TestCase`
- 写几个 `test_` 方法
- 用断言验证结果
- 用 `assertRaises` 测异常
- 用 `setUp` 做测试准备

当你能独立写出上面几个小案例时，已经可以开始给自己的项目补基础测试了。  
后面再逐步加入 `subTest`、`skip`、`mock`，就能覆盖绝大多数日常开发场景。
