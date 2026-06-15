//  {
//     "semi": true,
//         "trailingComma": "none",
//             "singleQuote": true,
//                 "printWidth": 80,
//                     "tabWidth": 2,
//                         "useTabs": false,
//                             "bracketSpacing": true,
//                                 "arrowParens": "avoid",
//                                     "spaceBeforeFunctionParen": false
// }

// ✅ 正确的 .prettierrc.js 写法
// {
//   "semi": false,
//   "singleQuote": true,
//   "printWidth": 120,
//   "tabWidth": 2,
//   "useTabs": false,
//   "trailingComma": "none",
//   "bracketSpacing": true,
//   "arrowParens": "avoid",
//   "htmlWhitespaceSensitivity": "ignore",
//   "endOfLine": "auto"
// }

// .prettierrc.js
module.exports = {
  semi: false,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'none',
  printWidth: 100,
  spaceBeforeFunctionParen: false
}
