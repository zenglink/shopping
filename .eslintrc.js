module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/essential',
    '@vue/standard'
    // 让ESLint兼容Prettier规则
    // 'plugin:prettier/recommended' // ✅ 这才是你能用的
  ],
  parserOptions: {
    parser: '@babel/eslint-parser'
  },
  rules: {
    indent: 'off', // 关闭缩进检查
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    // 'space-before-function-paren': ['error', 'error'],
    'space-before-function-paren': 'off',

    // 原来的缩进删掉，换成这一行
    // indent: ['error', 2], // 👈 强制 12 个空格缩进

    'vue/multi-word-component-names': 'warn' // 警告单词组件名
  }
}
