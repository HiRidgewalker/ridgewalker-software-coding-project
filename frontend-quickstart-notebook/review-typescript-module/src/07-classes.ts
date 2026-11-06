/*
类与面向对象支持

即使现代前端更常写函数式代码，类仍然是 TypeScript 需要掌握的一部分，
尤其在面向对象设计、旧项目、框架源码和后端代码里仍然常见。
*/

interface Logger {
  log(message: string): void;
}

abstract class Animal {
  constructor(protected name: string) {}

  abstract speak(): void;

  move(): void {
    console.log(`${this.name} moves`);
  }
}

class Dog extends Animal implements Logger {
  constructor(
    name: string,
    private age: number,
    public readonly breed: string
  ) {
    super(name);
  }

  speak(): void {
    console.log(`${this.name} barks`);
  }

  log(message: string): void {
    console.log(`[Dog:${this.name}] ${message}`);
  }

  getAge(): number {
    return this.age;
  }
}

const dog = new Dog("Lucky", 3, "Corgi");

dog.move();
dog.speak();
dog.log("class members can have access modifiers");
console.log("age:", dog.getAge());
console.log("breed:", dog.breed);

/*
易混点：
- public / private / protected 是 TypeScript 提供的成员可见性控制。
- abstract class 不能直接实例化，它的作用是定义“必须被子类实现的能力”。
- 构造函数参数前加修饰符，会自动创建并初始化同名属性。
*/

export {};
