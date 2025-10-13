<script>
import {defineComponent} from "vue";

export default defineComponent({
  props: {
    title: {
      type: String,
      default: null,
    },
    icon: {
      type: String,
      default: null,
    }
  },
  data() {
    return {}
  },
  computed: {},
  methods: {

  }
})
</script>
<template>
  <v-row class="border-thin rounded px-3 pt-3 pb-0 mt-7 mb-7 ml-1 mr-1" >
     <div class="wrapTitle">
        <div class="inTitle pl-3 pr-3">
          <v-icon :icon="icon" v-if="icon"/>
            {{ title }}
        </div>
      </div>
      <slot></slot>
  </v-row>
</template>

<style scoped>
.wrapTitle {
  position: relative;
  width: 0px;
  height: 0px;
}
.inTitle {
  color: var(--v-theme-on-surface);
  position: absolute;
  top: -22px;
  left: 0;
  white-space: nowrap;
  border-right: 0px solid var(--color-border);
  border-left: 0px solid var(--color-border);
  border-radius: 5px;
  background-color: #f5f5f5;
}
</style>