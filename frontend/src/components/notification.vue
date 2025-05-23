<script>
import {defineComponent} from "vue";

export default defineComponent({
  emits: ['close'],
  props: {
    notifyObj: {
      type: Object,
    },
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      notificationShow: this.show
    }
  },
  computed: {
    notificationText() {
      return this.notifyObj?.text || this.notifyObj?.error?.response?.data?.text || 'Error'
    },
    notificationDetail() {
      return this.notifyObj?.detail || this.notifyObj?.error?.response?.data?.detail || ''
    },
    notificationTimeout() {
      return this.notifyObj?.timeout || 5000
    },
    notificationIcon() {
      return this.notifyObj?.error ? 'mdi-alert-circle-outline' : this.notifyObj?.icon;
    },
    notificationColor() {
      switch (this.notifyObj?.status) {
        case 'error':
          return 'red-darken-4';
        case 'info':
          return 'blue-darken-1';
        case 'warn':
          return 'orange-darken-1';
        case 'ok':
          return 'light-green-darken-4';
        default:
          if (this.notifyObj?.error?.status === 'error') {
            return 'red-darken-4';
          }
          return this.notifyObj?.color
      }
    },
  },
  watch: {
    notifyObj() {
      this.notificationShow = true
    }
  }
})
</script>
<template>
  <v-snackbar
      v-model="notificationShow"
      :timeout="notificationTimeout"
      :color="notificationColor"
      :multi-line="true"
      close-on-content-click
  >
    <div class="d-flex flex-row">
      <v-sheet class="mr-2" color="transparent">
        <v-icon :icon="notificationIcon" size="x-large" v-if="notificationIcon"/>
      </v-sheet>
      <v-sheet class="ml-5 pt-1 pr-7" color="transparent">
        <strong>{{notificationText }}</strong>
        <ul v-if="Array.isArray(notificationDetail)" class="ma-0 pa-0">
          <li v-for="(it, index) in notificationDetail"
              :key="index">
            {{ it.msg }}: {{ it.loc[1]}}
          </li>
        </ul>
        <p v-else>
          {{ notificationDetail }}
        </p>
      </v-sheet>
    </div>
  </v-snackbar>
</template>
