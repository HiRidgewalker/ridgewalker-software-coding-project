// JavaScript 异常捕获回顾
// 运行方式: node 02-error-handling.js

function section(title) {
  console.log(`\n=== ${title} ===`);
}

section("try...catch");

// JSON.parse 会把 JSON 字符串转成 JavaScript 对象。
// 这里故意传入一个非法 JSON 字符串，让它抛出 SyntaxError。
try {
  JSON.parse("{ invalid json }");
} catch (error) {
  // catch (error) 中的 error 只是一个变量名。
  // 它用来接收“被抛出的值”，常见命名还有 err、e。
  console.log("捕获到错误:");

  // 对于内置异常，这里通常是 "object"，
  // 因为大多数异常都是 Error 或其子类的实例对象。
  console.log("typeof error:", typeof error);

  // name 表示错误类型名，例如 SyntaxError、TypeError、Error。
  console.log("name:", error.name);

  // message 表示错误信息，是最常读取的字段之一。
  console.log("message:", error.message);

  // stack 表示调用栈，调试时非常有用。
  console.log("是否有 stack:", Boolean(error.stack));
}

section("throw 主动抛出异常");

function divide(a, b) {
  if (b === 0) {
    // Error 是 JavaScript 标准错误对象的基础类之一。
    // new Error("...") 的含义是: 基于 Error 这个类，创建一个错误实例对象。
    //
    // 这里的 new 可以先简单理解为:
    // 1. 按照 Error 这个“模板/类”创建一个新对象
    // 2. 把 message 等属性放到这个对象上
    // 3. 返回这个新创建的对象
    //
    // throw 的作用是把这个错误对象抛出去，中断当前函数执行。
    throw new Error("除数不能为 0");
  }
  return a / b;
}

try {
  console.log("10 / 2 =", divide(10, 2));
  console.log("10 / 0 =", divide(10, 0));
} catch (error) {
  console.log("divide 出错:", error.message);
}

section("自定义错误类型");

// class 是 ES6 的类语法，用来描述一类对象的公共结构和行为。
// 这里定义了一个 ValidationError 类，它继承自 Error。
class ValidationError extends Error {
  constructor(message) {
    // super(message) 会调用父类 Error 的构造函数。
    // 如果不调用 super，在子类中就不能使用 this。
    super(message);

    // 默认情况下，继承 Error 后 name 可能还是 "Error"，
    // 所以这里手动改成更明确的错误类型名。
    this.name = "ValidationError";
  }
}

function validateUser(user) {
  if (!user.name) {
    // new ValidationError(...) 表示创建一个自定义错误对象实例。
    // 这个实例既是 ValidationError 的实例，也是 Error 的实例。
    throw new ValidationError("name 字段不能为空");
  }
  if (user.age < 0) {
    throw new ValidationError("age 不能小于 0");
  }
  return true;
}

try {
  validateUser({ age: 18 });
} catch (error) {
  console.log("捕获到的 error.name:", error.name);

  // instanceof 用来判断“某个对象是否由某个类创建出来”。
  // 可以先把它理解成: error 是不是 ValidationError 这个类的实例。
  console.log(
    "error instanceof ValidationError:",
    error instanceof ValidationError,
  );

  // 因为 ValidationError 继承了 Error，
  // 所以它的实例同时也属于 Error。
  console.log("error instanceof Error:", error instanceof Error);

  if (error instanceof ValidationError) {
    console.log("校验失败:", error.message);
  } else {
    console.log("未知错误:", error.message);
  }
}

section("finally");

function simulateTask() {
  console.log("任务开始");
  try {
    throw new Error("任务执行失败");
  } catch (error) {
    console.log("catch 中处理:", error.message);
  } finally {
    // finally 不管是否出错，通常都会执行。
    // 常用于关闭文件、断开连接、清理状态等收尾操作。
    console.log("finally 一定会执行，常用于资源释放");
  }
}

simulateTask();

section("异步异常: async / await");

function mockApi(shouldFail) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      if (shouldFail) {
        // reject 相当于让这个 Promise 进入失败状态。
        // 这里把 Error 实例作为失败原因传出去。
        reject(new Error("接口请求失败"));
      } else {
        resolve({ code: 200, data: ["A", "B"] });
      }
    }, 100);
  });
}

async function runAsyncExamples() {
  try {
    const successResult = await mockApi(false);
    console.log("成功结果:", successResult);

    // await 一个被 reject 的 Promise 时，会像同步 throw 一样进入 catch。
    await mockApi(true);
  } catch (error) {
    console.log("异步捕获到错误:", error.message);
  }
}

runAsyncExamples().then(function () {
  section("小结");
  console.log("new + 类名 表示基于这个类创建一个实例对象。");
  console.log("Error 是内置错误类，ValidationError 是我们自定义的错误类。");
  console.log("catch 接收到的通常是错误对象，但理论上也可以是任何被 throw 的值。");
});
