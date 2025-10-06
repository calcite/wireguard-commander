<template>
  <v-text-field
    v-model="formattedIPAddress"
    :label="label"
    :hint="hint"
    :rules="ipAddressRules"
    :class="class"
    prepend-icon="mdi-ip-outline"
    persistent-hint
  >
    <template #append-inner>
      <slot name="append-inner"></slot>
    </template>
  </v-text-field>
</template>

<script>
export default {
  name: 'IPAddressInput',
  props: {
    value: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: 'IP Address'
    },
    hint: {
      type: String,
      default: 'Enter IP address (e.g. 192.168.1.5)'
    },
    class: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      formattedIPAddress: this.value,
      ipAddressRules: [
          v => v === undefined || v === '' || v === null || this.isValidIPv4(v) || 'IP address must be in a valid format.'
      ]
    };
  },
  methods: {
    isValidIPv4(ip) {
      const regex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
      return regex.test(ip);
    }
  },
  watch: {
    value(newValue) {
      this.formattedIPAddress = newValue;
    }
  }
};
</script>

<style scoped>
</style>
