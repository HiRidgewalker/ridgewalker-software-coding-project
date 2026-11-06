/*
联合类型与类型收窄

TypeScript 的核心价值之一是：
一个值可能有多种形态，但你必须在使用前先判断清楚。
*/

type LoadingState = "idle" | "loading" | "success" | "error";

function printState(state: LoadingState): void {
  console.log("state:", state);
}

type ApiResponse =
  | { ok: true; data: string[] }
  | { ok: false; error: string };

function handleResponse(response: ApiResponse): void {
  if (response.ok) {
    console.log("data count:", response.data.length);
  } else {
    console.log("error:", response.error);
  }
}

function padLeft(value: string, padding: string | number): string {
  if (typeof padding === "number") {
    return " ".repeat(padding) + value;
  }

  return padding + value;
}

class Bird {
  fly() {
    console.log("Bird is flying");
  }
}

class Fish {
  swim() {
    console.log("Fish is swimming");
  }
}

function moveAnimal(animal: Bird | Fish): void {
  if (animal instanceof Bird) {
    animal.fly();
    return;
  }

  animal.swim();
}

type Admin = {
  name: string;
  permissions: string[];
};

type Guest = {
  name: string;
  expiresAt: Date;
};

function printVisitorInfo(visitor: Admin | Guest): void {
  if ("permissions" in visitor) {
    console.log(`${visitor.name} is admin: ${visitor.permissions.join(", ")}`);
    return;
  }

  console.log(`${visitor.name} is guest until ${visitor.expiresAt.toISOString()}`);
}

printState("loading");
handleResponse({ ok: true, data: ["ts", "js"] });
handleResponse({ ok: false, error: "network error" });
console.log(padLeft("TS", 4));
console.log(padLeft("TS", ">> "));
moveAnimal(new Bird());
moveAnimal(new Fish());
printVisitorInfo({ name: "Root", permissions: ["read", "write"] });
printVisitorInfo({ name: "Visitor", expiresAt: new Date("2026-04-01") });

/*
易混点：
- 联合类型不是“同时满足多种类型”，而是“可能是其中之一”。
- 收窄发生在控制流里；判断写得越清楚，TypeScript 推断得越准确。
- 给联合类型设计一个可判别字段，是最稳定的建模方式。
*/

export {};
