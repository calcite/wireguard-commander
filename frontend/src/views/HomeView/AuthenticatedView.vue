<script>
import {defineComponent} from "vue";
import Page from "@/components/page.vue";


export default defineComponent({
  name: 'AuthenticatedView',
  components: {Page},
  props: {},
  data() {
    return {
      isDetailShown: false,
    }
  },
  methods: {
  }
})
</script>

<template>
  <page v-model="isDetailShown" icon="mdi-account"
        title="Home panel"
        description="User info.">

    <template #panel>
      <pre>{{ JSON.stringify($auth.user, null, "  ") }}</pre>
    </template>


    <v-btn color="primary" text="Toggle" @click="isDetailShown = !isDetailShown" />
  </page>
</template>
