<script>
import {defineComponent} from "vue";
import Info from "@/components/info.vue";
import Notification from "@/components/notification.vue";
import DeleteConfirmation from "@/components/deleteConfirmation.vue";
import UsergroupPermissions from './networkPermissions.vue'
import IpField from "@/components/ipField.vue";

export default defineComponent({
  components: {DeleteConfirmation, UsergroupPermissions, Notification, Info, IpField},
  emits: ['canceled', 'deleted', 'created', 'updated', 'resize'],
  props: {
    selected: {
      type: Object,
    }
  },
  data() {
    return {
      deleteConfirmationOpen: false,
      voucherServerOpen: false,
      selectedBackup: null,
      notify: null,
      isFormValid: null,
      groupPermissions: false,
      selectedUserGroup: null,
      allPermissions: {},
      allUserGroups: [],
      fullSize: false,
    }
  },
  watch: {
    selected(newVal) {
      this.selectedBackup = JSON.stringify(newVal)  // deep copy
    },
    voucherServerOpen(newVal) {
      if (!newVal) {
        if (!this.selected.voucher_ip) {
          this.selected.voucher_enabled = false
        }
      }
    }
  },
  mounted() {
    this.$api.get('/api/interfaces/permissions').then(result => {
      this.allPermissions = result.data;
    })
    this.$api.get('/api/users-groups/').then(result => {
      this.allUserGroups = result.data;
    })
  },
  computed: {
    avaiableUserGroups() {
      if (!this?.selected || !this.selected?.user_groups) {
        return this.allUserGroups
      }
      const ids = this?.selected?.user_groups.map(it => it.id)
      return this.allUserGroups.filter(it => !ids.includes(it.id))
    },
  },
  methods: {
    doCancel() {
      const back = JSON.parse(this.selectedBackup)
      for (let name in back) {
        this.selected[name] = back[name]
      }
      console.log(this.selected, back)
      this.$emit('canceled', this.selected)
    },
    async doDelete() {
      const result = await this.$apiStore.delete('Interface', this.selected)
      this.notify = result.notification;
      if (this.notify?.status !== 'error') {
        this.$emit('deleted', this.selected)
      }
    },
    async doSubmit() {
      if (this.$refs.userForm.validate()) {
        const result = await this.$apiStore.submit('Interface', this.selected)
        this.notify = result.notification;
        if (this.notify?.status !== 'error') {
          if (result?.created) {
            Object.assign(this.selected, result.updated)
            this.$emit('created', result.created)

          } else {
            Object.assign(this.selected, result.updated)
            this.$emit('updated', result.updated)
          }
        }
      }
    },
    setUsergroup(userGroup) {
      this.selectedUserGroup = userGroup
    },
    addUsergroup() {
      this.selectedUserGroup = {
        name: null,
        desc: null,
        permissions: []
      }
    },
    doUserGroupClose() {
      if (this.selectedUserGroup?.permissions.length === 0) {
        this.selected.user_groups = this.selected.user_groups.filter(it => it.id !== this.selectedUserGroup?.id)
      }
      console.log(this.selected.user_groups)
      this.setUsergroup(null)
    },
    doAddNewUserGroup() {
      if (!this.selected?.user_groups) {
        this.selected.user_groups = new Array()
      }
      this.selected.user_groups.push(this.selectedUserGroup)
    },
    doFullSizeToggle() {
      this.fullSize = !this.fullSize
      this.$emit('resize', this.fullSize)
    },
    joinPermissions(perms) {
      return perms ? perms.map(it => this.allPermissions[it].name).join(', ') : ''
    },
    voucherServerOnChange(event) {
      if (this.selected?.voucher_enabled) {
        this.voucherServerOpen = true
      }
    }
  }
})
</script>

<template>
  <v-card flat color="transparent" v-if="selected !== null"
          :prepend-icon="$router.currentRoute._value.meta.icon"
          :title="selected.server_name"
  >
    <template #append>
        <v-tooltip bottom>
        <template v-slot:activator="{ props }">
          <v-icon v-bind="props"
                  :icon="!fullSize ? 'mdi-chevron-double-left' : 'mdi-chevron-double-right'"
                  @click="doFullSizeToggle"></v-icon>
        </template>
        <slot>
          Advanced options
        </slot>
      </v-tooltip>
    </template>
    <v-card-text>
      <v-form ref="userForm" v-model="isFormValid" lazy-validation :class="!fullSize ? ['smallPanel'] : []">
        <v-row>
        <v-col cols="auto" md="2">
        <v-text-field
            v-model="selected.server_name"
            label="Server Name"
            :rules="[v => !!v || 'Server name is required']"
            default-value="default"
            :counter="$apiStore.getMaxLength('InterfaceUpdate', 'server_name')"
        >
          <template #append-inner>
            <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
          </template>
        </v-text-field>
        </v-col>
        <v-col cols="auto" md="2">
        <v-text-field
            v-model="selected.public_endpoint"
            label="Public Endpoint"
            :rules="[v => !!v || 'Public endpoint is required']"
            default-value="default"
            :counter="$apiStore.getMaxLength('InterfaceUpdate', 'public_endpoint')"
        >
          <template #append-inner>
            <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
          </template>
        </v-text-field>
        </v-col>
        <v-col cols="auto" md="2">
        <v-text-field
            v-model="selected.listen_port"
            label="Listen Port"
            prepend-icon="mdi-crop-portrait"
            :rules="[v => Number(v) >= -1 || 'Wrong port.']"
            type="number"

        >
          <template #append-inner>
            <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
            <info>
              UDP port on which the WireGuard server will listen.
            </info>
          </template>
        </v-text-field>
        </v-col>
        <v-col cols="auto" md="2">
        <v-text-field
            v-model="selected.interface_name"
            label="Interface Name"
            prepend-icon="mdi-cable-data"
            :rules="[v => !!v || 'Interface name is required']"
            :counter="$apiStore.getMaxLength('InterfaceUpdate', 'interface_name')"
            hint="e.g. wg0"
            persistent-hint
        >
          <template #append-inner>
            <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
            <info>
              The server interface has to be unique per server.
            </info>
          </template>
        </v-text-field>
        </v-col>
        <v-col cols="auto" md="4">
        <ip-field
            v-model="selected.address"
            label="IP address"
        >
          <template #append-inner>
            <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
            <info>
              The public IP of the wireguard interface.
            </info>
          </template>
        </ip-field>
        </v-col>
        <v-col cols="auto" md="4">
        <v-container class="border-thin rounded mt-3 pt-2 pb-6">
          <h3 class="text-truncate mb-2 d-flex justify-space-between">
            <span>
              <v-icon icon="mdi-account-group"
                      class="mr-3"
                      style="vertical-align: middle"
              ></v-icon>
              User groups
            </span>
             <v-icon icon="mdi-plus-box-outline"
                     @click="addUsergroup"
                     :disabled="avaiableUserGroups.length === 0"/>
          </h3>
          <v-row>
            <v-col
                v-for="item in selected.user_groups"
                :key="item.name"
                cols="12"
                md="6"
                sm="12"
            >
              <v-sheet border rounded
                       class="mx-auto cursor-pointer"
                       @click="setUsergroup(item)"
              >
                  <v-list density="compact">
                    <h4 class="ml-3">{{item.name}}</h4>
                    <p class="text-caption px-3">
                      {{ joinPermissions(item.permissions) }}
                    </p>
                  </v-list>
              </v-sheet>
            </v-col>
          </v-row>
        </v-container>
        </v-col>
        </v-row>
      </v-form>
    </v-card-text>
    <v-card-actions class="d-flex justify-space-between mt-5">
      <div>
        <v-btn
            text="Save"
            class="ml-3 my-1"
            color="primary"
            :disabled="!isFormValid"
            @click="doSubmit"/>
        <v-btn
            class="ml-3 my-1"
            @click="doCancel">Cancel
        </v-btn>
      </div>
      <div>
        <v-btn
            v-if="!selected.is_admin && !selected.is_default && selected.id"
            class="mr-3 my-1"
            @click="deleteConfirmationOpen=true"
            prepend-icon="mdi-trash-can-outline"
            color="red-darken-4">Delete
        </v-btn>
      </div>
    </v-card-actions>
  </v-card>

  <delete-confirmation
      v-model="deleteConfirmationOpen"
      objectName="network"
      :name="selected?.name"
      @delete="doDelete"
  >
    <template #text>
      Are you sure that you want to delete this network and all registered devices in this network?
    </template>
  </delete-confirmation>
  <usergroup-permissions
    v-model="selectedUserGroup"
    :allPermissions="allPermissions"
    :avaiableUserGroups="avaiableUserGroups"
    @close="doUserGroupClose"
    @newGroup="doAddNewUserGroup"
  />
  <notification :notify-obj="notify" />
</template>


<style scoped>
.smallPanel .v-row {
    display: block !important;
    gap: 0 !important;
  }
.smallPanel .v-col-auto {
    display: block !important;
    max-width: 100% !important;
    flex: none !important;
  }
</style>