import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView/View.vue'
import UsersView from '../views/UsersView.vue'

const permsContain = (text) => (perms) => perms.some(it => it === 'admin:all' || it.includes(text))

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Home",
      component: HomeView,
      meta: {
        icon: 'mdi-view-dashboard',
        menu: true
      }
    }, {
      path: "/logged-in",
      name: "Users",
      component: UsersView,
      meta: {
        permission: 'admin:all',
        icon: 'mdi-account-outline',
        menu: true,
      }
    }
  ],
})

export default router
