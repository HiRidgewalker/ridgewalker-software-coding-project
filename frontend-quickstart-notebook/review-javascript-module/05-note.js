a = 1;
console.log("hello world");
// switch (a) {
//     case 1:
//         console.log('a is 1')
//         break
//     case 2:
//         console.log('a is 2')
//         break
//     default:
//         console.log('a is not 1 or 2')
// }

// 1. switch 语句会从上到下执行，直到找到匹配的 case 语句，如果没有找到匹配的 case 语句，则执行 default 语句。

function funcOne() {
  switch (a) {
    case 1:
      return "a";
    case 2:
      return "b";
    default:
      return "c";
  }
}

result = funcOne();

console.log(result)