<script>
import {defineComponent} from "vue";

export default defineComponent({
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    title: null,
    description: null,
    icon: null,
    detailPanelWidth: {
      type: String,
      default: '20vw',
    }
  },
  data() {
    return {}
  },
  computed: {
    currentPageIcon() {
      return this.icon ? this.icon : this.$router.currentRoute._value.meta.icon
    },
    currentPageTitle() {
      return this.title ? this.title : this.$router.currentRoute._value.name
    },
    currentPageDesc() {
      return this.description ? this.description : this.$router.currentRoute._value.meta.description
    },
    localShowPanel: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    }
  },
  watch: {}
})
</script>

<template>
  <v-navigation-drawer
      v-model="localShowPanel"
      :location="!$vuetify.display.mobile ? 'right' : 'top'"
      style="background-color: #f5f5f5;">
    <slot name="panel"></slot>
  </v-navigation-drawer>
  <v-card flat :subtitle="currentPageDesc">
    <template v-slot:prepend>
      <v-icon class="text-h3 pr-3" :icon="currentPageIcon" />
    </template>
    <template v-slot:title>
      <span class="text-h5">
          {{ currentPageTitle }}
      </span>
    </template>
    <template v-slot:subtitle v-if="currentPageDesc">
      <span>{{ currentPageDesc }}</span>
    </template>
    <template v-slot:append>
      <slot name="buttons"></slot>
    </template>
  </v-card>
  <slot></slot>
</template>

<style scoped>
.v-navigation-drawer--active {
  min-width: v-bind('detailPanelWidth');
  min-height: 100vh;
}
</style>
