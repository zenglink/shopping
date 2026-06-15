import { changeCount, delSelect, getCartList } from '@/api/cart'
import { Toast } from 'vant'
export default {
  namespaced: true,
  state() {
    return {
      cartList: []
    }
  },
  mutations: {
    // 提供一个设置 cartList 的 mutation
    setCartList(state, newList) {
      state.cartList = newList
    },
    toggleCheck(state, goodsId) {
      const goods = state.cartList.find((item) => item.goods_id === goodsId)
      goods.isChecked = !goods.isChecked
    },
    toggleAllCheck(state, flag) {
      state.cartList.forEach((item) => {
        item.isChecked = flag
      })
    },
    changeCount(state, { goodsId, value }) {
      const obj = state.cartList.find((item) => item.goods_id === goodsId)
      obj.goods_num = value
    }
  },
  actions: {
    async getCartAction(context) {
      const { data } = await getCartList()
      console.log(data)
      data.list.forEach((item) => {
        item.isChecked = true
      })
      context.commit('setCartList', data.list)
    },
    async changeCountAction(context, obj) {
      const { goodsId, value, skuId } = obj
      // 先本地修改
      context.commit('changeCount', {
        goodsId,
        value
      })
      // 在同步到后台
      await changeCount(goodsId, value, skuId)
    },
    async delSelect(context) {
      const selCartList = context.getters.selCartList
      const cartIds = selCartList.map((item) => item.id)
      await delSelect(cartIds)
      Toast('删除成功')
      // 重新渲染购物车数据
      context.dispatch('getCartAction')
    }
  },
  getters: {
    // 求所有的商品累加总数
    cartTotal(state) {
      return state.cartList.reduce((sum, item) => item.goods_num, 0)
    },
    // 选中的商品项
    selCartList(state) {
      return state.cartList.filter((item) => item.isChecked)
    },
    // 选中的总数
    selCount(state, getters) {
      return getters.selCartList.reduce((sum, item) => sum + item.goods_num, 0)
    },
    // 选中的总价
    selPrice(state, getters) {
      return getters.selCartList
        .reduce((sum, item) => {
          return sum + item.goods_num * item.goods.goods_price_min
        }, 0)
        .toFixed(2)
    },
    // 是否全选
    isAllChecked(state) {
      return state.cartList.every((item) => item.isChecked)
    }
  }
}
