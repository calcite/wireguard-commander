import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueKeyCloak, { useKeycloak }  from '@dsb-norge/vue-keycloak-js'
import api from './services/api'
import App from './App.vue'
import router from './router'
import VuetifyPlugin from './plugins/vuetify'
import { useAuthStore } from './stores/authStore'



function initializeTokenInterceptor () {
  api.interceptors.request.use(config => {
    const keycloak = useKeycloak()
    if (keycloak.authenticated) {
      config.headers.Authorization = `Bearer ${keycloak.token}`
    }
    return config
  }, error => {
    return Promise.reject(error)
  })
}


const app = createApp(App)
app.use(createPinia())
app.use(VuetifyPlugin)
const authStore = useAuthStore()

app.use(VueKeyCloak, {
    init: {
      onLoad: 'check-sso'
    },
    onReady (keycloak) {
      console.log('Keycloak ready')
      initializeTokenInterceptor()
      authStore.initOauth(keycloak).then((res) => {
        if (!res) {
          console.error('User not authenticated')
          return
        }
        console.log('User data initialized')
      }).catch((error) => {
        console.error('Error initializing user data:', error)
      })
    },
    onAuthError (error) {
      console.error('Authentication error:', error)
      authStore.clearUserData()
    },
    onAuthLogout (keycloak) {
      console.log('User logged out')
      authStore.clearUserData()
    },
    onAuthRefreshSuccess (keycloak) {
      console.log('Token refreshed')
      authStore.initOauth(keycloak).then(() => {
        console.log('User data initialized')
      }).catch((error) => {
        console.error('Error initializing user data:', error)
      })
    },
    onAuthRefreshError (error) {
      console.error('Token refresh error:', error)
      authStore.clearUserData()
    },
  })


app.use(router)

app.mount('#app')
