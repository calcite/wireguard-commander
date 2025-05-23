<script>
import { useKeycloak } from '@dsb-norge/vue-keycloak-js'
import {defineComponent} from "vue";
import api from "@/services/api";
import { useAuthStore } from '@/stores/authStore'


export default defineComponent({
  setup() {
    const keycloak = useKeycloak()
    const authStore = useAuthStore()
    return { keycloak, authStore }
  },
  props: {},
  data() {
    return {}
  },
  methods: {
    async test() {
      // this.$socket.emit('test', {payload: 'AAA'})
      const response = await api.get('/me')
      console.log(response.data)
    },
    login() {
      this.keycloak.keycloak.login()
    },
    logout() {
      this.keycloak.keycloak.logout()
    },
  }
})
</script>

<template>
  <p>{{ keycloak.authenticated }}</p>
  <button @click="login()" v-if="!keycloak.authenticated">Login</button>
  <button @click="logout()" v-if="keycloak.authenticated">Logout</button>

  <textarea :value="JSON.stringify(keycloak, null, 4)" />
  <button @click="test()">Test</button>
</template>
