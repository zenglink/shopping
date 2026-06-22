import Vue from 'vue'
import VueRouter from 'vue-router'
import layout from '@/views/layout/index.vue'
import store from '@/store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    component: layout,
    redirect: 'home',
    children: [
      { path: 'home', component: () => import('@/views/layout/home.vue') },
      { path: 'cart', component: () => import('@/views/layout/cart.vue') },
      { path: 'user', component: () => import('@/views/layout/user.vue') },
      { path: 'category', component: () => import('@/views/layout/category.vue') }
    ]
  },
  { path: '/myorder', component: () => import('@/views/myorder/index.vue') },
  { path: '/login', component: () => import('@/views/login/index.vue') },
  { path: '/pay', component: () => import('@/views/pay/index.vue') },
  // 动态路由传参，确定将来是哪个商品，路由参数中携带id
  { path: '/prodetail/:id', component: () => import('@/views/prodetail/index.vue') },
  { path: '/search', component: () => import('@/views/search/index.vue') },
  { path: '/searchlist', component: () => import('@/views/search/list.vue') }
]

const router = new VueRouter({
  // mode: 'history',
  base: process.env.BASE_URL,
  routes
})

const authUrls = ['/pay', '/myorder']
router.beforeEach((to, from, next) => {
  // console.log(to, from, next)
  // 看 to.path是否在authUrls 中出现过
  if (!authUrls.includes(to.path)) {
    // 非权限页面，直接放行
    next()
    return
  }

  // 是权限页面，需要判断token
  const token = store.getters.token
  console.log(token)

  if (token) {
    next()
  } else {
    next('/login')
  }
})

export default router
