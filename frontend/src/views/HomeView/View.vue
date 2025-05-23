<script>
import {defineComponent, ref} from "vue";
import NonAuthenticatedView from "./NonAuthenticatedView.vue";
import AuthenticatedView from "./AuthenticatedView.vue";
import Notification from "@/components/notification.vue";

export default defineComponent({
  components: {Notification, NonAuthenticatedView, AuthenticatedView},
  data() {
    return {
      notifyMessage: null,
    }
  },
})
</script>

<template>
  <NonAuthenticatedView v-if="!$auth.authenticated" @notify="notifyMessage = $event" />
  <AuthenticatedView v-else />
  <Notification :notify-obj="notifyMessage" :show="!!notifyMessage" />
</template>

