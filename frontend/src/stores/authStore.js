import { defineStore } from 'pinia'
import api from '@/services/api';


export const useAuthStore = defineStore("storeAuth", {
  // persistent: true,
  state: () => {
    return {
      authenticated: false,
      user: {},
    }
  },
  getters: {},
  actions: {
    // Initialize Keycloak OAuth
    async initOauth(keycloak) {
      if (!keycloak.authenticated) {
        this.clearUserData();
        return false;
      }
      const response = await api.get('/me');
      if (response.status !== 200) {
        this.clearUserData();
        return false;
      }
      this.user = response.data
      this.authenticated = true;
      return true;
    },

    // Clear user's store data
    clearUserData() {
      this.authenticated = false;
      this.user = {};
    },

    // return True if the role has been assigned to this user
    isRoleAssigned(role) {
       if (this?.user?.roles) {
         return this.user.realm_access.includes(role) || this.user.resource_access.includes(role)
       }
       return false
    }
  }
});
