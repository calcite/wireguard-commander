import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
    path: "/",
    name: "Login",
    component: HomeView,
    meta: {
      icon: 'mdi-login',
      menu: true
    }
  },
  // {
  //   path: "/vouchers",
  //   name: "Vouchers",
  //   component: VouchersView,
  //   props: (route) => ({
  //     network_id: route.query?.network_id,
  //     network_name: route.query?.network_name,
  //     action: route.query?.action
  //   }),
  //   meta: {
  //     permission: (perms) => perms.some(it => it === 'admin:all' || it.includes('voucher')), //'user:authenticated',
  //     icon: 'mdi-ticket-outline',
  //     menu: true,
  //   }
  // }
  ],
})

export default router
