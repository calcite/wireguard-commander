import { createRouter, createWebHistory } from 'vue-router'
import { useKeycloak }  from '@dsb-norge/vue-keycloak-js'
import HomeView from '../views/HomeView/View.vue'
import UsersView from '../views/UsersView.vue'

const permsContain = (text) => (perms) => perms.some(it => it === 'admin:all' || it.includes(text))

const keycloak = useKeycloak()

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: () => keycloak.authenticated ? "Home" : "Login",
      component: HomeView,
      meta: {
        icon: () => keycloak.authenticated ? 'mdi-view-dashboard' : 'mdi-login',
        menu: true,
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
