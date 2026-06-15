<template>
  <div class="count-box">
    <button @click="handleMinus" class="minus">-</button>
    <input @change="handleChange" :value="value" class="inp" type="text" />
    <button @click="handleAdd" class="add">+</button>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {}
  },
  methods: {
    handleMinus() {
      if (this.value <= 1) {
        return
      }
      this.$emit('input', this.value - 1)
    },
    handleAdd() {
      this.$emit('input', this.value + 1)
    },
    handleChange(e) {
      const num = +e.target.value
      if (isNaN(num) || num < 1) {
        e.target.value = this.value
        return
      }
      this.$emit('input', num)
      console.log(e.target)
    }
  }
}
</script>

<style lang="less" scoped>
.count-box {
  display: flex;
  gap: 5px;
  width: 110px;
  .add,
  .minus {
    width: 30px;
    height: 30px;
    outline: none;
    border: none;
    background-color: #efefef;
  }
  .inp {
    width: 40px;
    height: 30px;
    outline: none;
    border: none;
    background-color: #efefef;
    text-align: center;
  }
}
</style>
