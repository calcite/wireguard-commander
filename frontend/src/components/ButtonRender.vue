<script>
import {defineComponent} from "vue";

export default defineComponent({
  name: 'ButtonRender',
  props: ['params'],
  methods: {
    onClick(event, ug, value) {
      event?.stopPropagation();
      if (ug?.action && typeof ug.action === 'function') {
        ug.action(value);
      } else {
        ug.value = value;
        if (this.params.onClick) this.params.onClick(ug);
      }
    }
  }
})
</script>
<template>
  <v-row >
    <v-col cols="auto" v-for="ug in params.items" :key="ug.action" >
      <v-icon
        v-if="ug.icon"
        :icon="ug.icon"
        :color="ug.color || ''"
        @click="onClick($event, ug, params.value)" />
    </v-col>
  </v-row>
</template>
