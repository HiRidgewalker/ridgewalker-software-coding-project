/*
类型别名、接口、枚举

这里解决“怎么给结构命名”的问题。
*/

type ProductId = string | number;

type Product = {
  id: ProductId;
  title: string;
  price: number;
};

interface CartItem extends Product {
  quantity: number;
}

interface Discountable {
  discount(rate: number): number;
}

class Book implements Discountable {
  constructor(private price: number) {}

  discount(rate: number): number {
    return this.price * (1 - rate);
  }
}

enum LegacyDirection {
  Up,
  Down,
  Left,
  Right
}

// 许多现代项目更偏向用字面量联合替代 enum，类型更直观。
type Direction = "up" | "down" | "left" | "right";

function move(direction: Direction): void {
  console.log("moving:", direction);
}

const cartItem: CartItem = {
  id: "book-1",
  title: "TypeScript Handbook",
  price: 88,
  quantity: 2
};

const discountedPrice = new Book(cartItem.price).discount(0.2);

console.log("cart item:", cartItem.title, "x", cartItem.quantity);
console.log("discounted price:", discountedPrice);
console.log("legacy enum right:", LegacyDirection.Right);
move("left");

/*
易混点：
- interface 更适合描述可扩展的对象结构。
- type 更通用，能表达联合类型、交叉类型、基础类型别名。
- enum 不是不能用，但在很多前端项目里，字面量联合通常更轻、更透明。
*/

export {};
