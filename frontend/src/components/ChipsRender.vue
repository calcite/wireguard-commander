<script>
import {defineComponent} from "vue";

export default defineComponent({
  name: 'ChipsRenderer',
  props: ['params'],
})
</script>
<template>
  <v-chip-group>
    <v-chip
        size="small"
        color="primary"
        v-for="ug in params.value"
        :key="ug.id"
        :text="ug.name"
    ></v-chip>
  </v-chip-group>
</template>
