import { createRouter, createWebHistory } from 'vue-router'
import MarketOverview from "../views/MarketOverview.vue"
import StockDetail from "../views/StockDetail.vue"
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'marketoverview',
      component: MarketOverview
    },
    {
      path: '/stockdetail',
      name: 'stockdetail',
      component: StockDetail

    }

  ]
})

export default router
