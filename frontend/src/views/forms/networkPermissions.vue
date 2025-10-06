<script>
import {defineComponent, ref} from "vue";
import Info from "@/components/info.vue";

export default defineComponent({
  components: {Info},
  emits: ['close', 'newGroup'],
  props: {
    modelValue: {
      type: [Object, null],
      default: () => null,
      required: false
    },
    maxWidth: {
      type: Number,
      default: 1000
    },
    allPermissions: {
      type: Object
    },
    avaiableUserGroups: {
      type: Array
    }
  },
  data() {
    return {
      showWindow: false,
      backupPermissions: [],
      disabled: {}
    }
  },
  computed: {
    getName() {
      return this.modelValue?.name ? `"${this.modelValue?.name} "` : ''
    },
    getWidth() {
      return this.modelValue?.id ? this.maxWidth : 500
    }
  },
  watch: {
    modelValue(newVal) {
      if (newVal !== null) {
        this.backupPermissions = [ ...newVal.permissions]

        for (let name in this.allPermissions) {
          const data = this.allPermissions[name]
          if(data?.required) {
            this.disabled[name] = (data.required.filter(it => this.modelValue.permissions.includes(it)).length === 0)
          }
        }
        for (let name of this.modelValue?.permissions) {
          for (let key of this.allPermissions[name]?.replacing || []) {
            this.disabled[key] = true
          }
        }
      } else {
        this.backupPermissions = null
      }
      this.showWindow = newVal !== null;
    },
    showWindow(newVal) {
      if (!newVal) {
        this.$emit('close')
      }
    }
  },
  methods: {
    doOK() {
      this.$emit('close')
    },
    doCancel() {
      this.modelValue.permissions = this.backupPermissions
      this.$emit('close')
    },
    doChange(event) {
      const name = event.target.value;
      const state = event.target.checked;
      if (this.allPermissions[name]?.replacing) {
        for (let key of this.allPermissions[name]?.replacing) {
          if (state) {
            this.modelValue.permissions = this.modelValue?.permissions.filter(it => it !== key)
          }
          this.disabled[key] = state
        }
      }
      for (let key in this.allPermissions) {
        const data = this.allPermissions[key]
        if (data?.required && data?.required.includes(name)) {
          if (!state) {
            this.modelValue.permissions = this.modelValue?.permissions.filter(it => it !== key)
          }
          this.disabled[key] = !state
        }
      }
    },
    doDelete() {
      this.modelValue.permissions = []
      this.$emit('close')
    },
    chooseNewUsergroup(id) {
      Object.assign(this.modelValue, this.avaiableUserGroups.filter(it => it.id === id)[0])
      this.$emit('newGroup')
    }
  },
})
//
</script>

<template>
  <v-dialog v-model="showWindow" :max-width="getWidth">
    <v-card :loading="allPermissions === null" v-if="modelValue?.id">
      <v-card-title class="text-h6 mt-3 pb-0">
       <v-icon icon="mdi-gavel" class="mr-3" /> Permissions for "{{ modelValue?.name}}" user group.
      </v-card-title>
      <v-card-text>
        <v-container fluid v-if="allPermissions !== null">
          <v-row>
            <v-col cols="12" md="4"
                   v-for="(val, key) in allPermissions"
                   :id="key">
              <v-switch
                  v-model="modelValue.permissions"
                  v-if="modelValue !== null"
                  :disabled="disabled[key]"
                  color="info"
                  :value="key"
                  :ref="key"
                  @change="doChange"
                  hide-details
              >
                <template v-slot:label>
                  <span class="mr-3">{{ val?.name }}</span>
                  <info>{{val?.desc}}</info>
                </template>
              </v-switch>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions class="d-flex justify-space-between px-8 pb-3">
        <div>
          <v-btn @click="doDelete" color="red-darken-4" prepend-icon="mdi-delete">Delete</v-btn>
        </div>
        <div>
          <v-btn @click="doOK" color="blue-darken-4">OK</v-btn>
          <v-btn @click="doCancel">Cancel</v-btn>
        </div>
      </v-card-actions>
    </v-card>
    <v-card v-else prepend-icon="mdi-gavel" title="Choose user group">
      <template v-slot:text>
        <v-container fluid>
            <v-select
                label="Select"
                :items="avaiableUserGroups"
                item-title="name"
                item-value="id"
                @update:modelValue="chooseNewUsergroup"
            ></v-select>
        </v-container>
      </template>
      <template v-slot:actions>
        <v-btn @click="doCancel">Cancel</v-btn>
      </template>
    </v-card>
  </v-dialog>
</template>
