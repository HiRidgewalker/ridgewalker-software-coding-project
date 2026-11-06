// JavaScript 类和对象回顾
// 运行方式: node 04-class-and-object.js

function section(title) {
  console.log(`\n=== ${title} ===`);
}

section("对象 Object");

// 对象可以理解成“键值对”的集合。
// 左边是属性名，右边是属性值。
const user = {
  name: "Alice",
  age: 20,
  sayHello: function () {
    console.log(`你好，我是 ${this.name}`);
  },
};

console.log("对象本身:", user);
console.log("读取属性 user.name:", user.name);
console.log("读取属性 user['age']:", user["age"]);
user.sayHello();

// 对象可以动态新增属性。
user.city = "Shanghai";
console.log("新增属性后:", user);

section("工厂函数");

// 工厂函数: 返回一个新对象。
// 本质上还是普通函数，只是它的返回值是对象。
function createBook(title, price) {
  return {
    title: title,
    price: price,
    printInfo: function () {
      console.log(`书名: ${this.title}, 价格: ${this.price}`);
    },
  };
}

const book1 = createBook("JavaScript Guide", 99);
book1.printInfo();

section("类 class");

// class 用来描述一类对象的共同结构和行为。
// 可以把类理解成“对象的模板”。
class Person {
  // constructor 是构造函数。
  // 当你执行 new Person("Tom", 18) 时，会自动调用 constructor。
  constructor(name, age) {
    // this 表示“当前创建出来的实例对象”。
    // 下面两行的意思是把参数挂到实例对象上。
    this.name = name;
    this.age = age;
  }

  // 写在类中的函数叫“方法”。
  // 所有实例都可以访问这些方法。
  introduce() {
    console.log(`我是 ${this.name}，今年 ${this.age} 岁`);
  }
}

// new Person("Tom", 18) 的含义可以先这样理解:
// 1. 创建一个新的空对象
// 2. 让这个对象按照 Person 类的规则初始化
// 3. 自动把 this 指向这个新对象
// 4. 最后返回这个新对象
const person1 = new Person("Tom", 18);
const person2 = new Person("Jerry", 20);

console.log("person1:", person1);
console.log("person2:", person2);
person1.introduce();
person2.introduce();

section("instanceof");

// instanceof 用来判断某个对象是不是某个类的实例。
console.log("person1 instanceof Person:", person1 instanceof Person);
console.log("person1 instanceof Object:", person1 instanceof Object);

section("继承 extends");

// Student 继承 Person，表示 Student 拥有 Person 的属性和方法。
class Student extends Person {
  constructor(name, age, grade) {
    // super(...) 用来调用父类 Person 的构造函数。
    // 先把父类负责的 name、age 初始化好。
    super(name, age);
    this.grade = grade;
  }

  study() {
    console.log(`${this.name} 正在学习`);
  }

  // 子类也可以重写父类方法。
  introduce() {
    console.log(`我是学生 ${this.name}，今年 ${this.age} 岁，年级是 ${this.grade}`);
  }
}

const student1 = new Student("Lucy", 16, "高一");
console.log("student1:", student1);
student1.introduce();
student1.study();
console.log("student1 instanceof Student:", student1 instanceof Student);
console.log("student1 instanceof Person:", student1 instanceof Person);

section("对象遍历");

for (const key in user) {
  console.log(`for...in -> ${key}:`, user[key]);
}

console.log("Object.keys(user):", Object.keys(user));
console.log("Object.values(user):", Object.values(user));
console.log("Object.entries(user):", Object.entries(user));

section("小结");
console.log("对象是具体的数据，类是创建对象的模板。");
console.log("new + 类名 表示创建这个类的实例对象。");
console.log("extends 表示继承，super 用来调用父类构造函数。");
