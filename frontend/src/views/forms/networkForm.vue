<script>
import {defineComponent} from "vue";
import Info from "@/components/info.vue";
import Notification from "@/components/notification.vue";
import DeleteConfirmation from "@/components/deleteConfirmation.vue";
import UsergroupPermissions from './networkPermissions.vue'
import IpField from "@/components/ipField.vue";
import Block from "@/components/block.vue";


export default defineComponent({
  components: {DeleteConfirmation, UsergroupPermissions, Notification, Info, IpField, Block},
  emits: ['canceled', 'deleted', 'created', 'updated', 'resize'],
  props: {
    selected: {
      type: Object,
    },
    fullsize: {
      type: Boolean,
      default: false,
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
          console.log(result)
          if (result?.created) {
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

        <block title="Basic settings" icon="mdi-cog-outline">
          <v-col cols="auto" md="2">
            <v-checkbox
                v-model="selected.enabled"
                density="compact"
                variant="outlined"
                hide-details="true"
                label="Enabled"
            />
          </v-col>

          <v-col cols="auto" md="2">
            <v-text-field
                v-model="selected.server_name"
                density="compact"
                variant="outlined"
                label="Server Name"
                class="min-w-150"
                :rules="[v => !!v || 'Server ID is required']"
                default-value="default"
                :counter="$apiStore.getMaxLength('InterfaceUpdate', 'server_name')"
            >
              <template #append-inner>
                <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="5" v-if="fullsize">
            <v-textarea
                v-model="selected.public_key"
                density="compact"
                variant="outlined"
                label="Public Key"
                rows="1"
                max-rows="5"
                auto-grow
            >
              <template #append-inner>
                <info>Public keys for this network.</info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="5" v-if="selected.private_key === null && fullsize">
            <v-textarea
                v-model="selected.private_key"
                density="compact"
                variant="outlined"
                label="Private Key"
                rows="1"
                max-rows="5"
                auto-grow
            >
              <template #append-inner>
                <info>Private keys for this network.</info>
              </template>
            </v-textarea>
          </v-col>

        </block>

        <block title="Server settings" icon="mdi-wrench-cog-outline">
          <v-col cols="auto" md="2">
            <v-text-field
                v-model="selected.interface_name"
                density="compact"
                variant="outlined"
                label="Interface Name"
                class="min-w-150"
                :rules="[v => !!v || 'Interface name is required']"
                :counter="$apiStore.getMaxLength('InterfaceUpdate', 'interface_name')"
                hint="e.g. wg0"
                persistent-hint
            >
              <template #append-inner>
                <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
                <info>
                  This interface name will be used on the server.<br>Make sure that this name is not already in use.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2">
            <ip-field
                v-model="selected.address"
                label="IP address"
                prepend-icon=""
                density="compact"
                variant="outlined"
                class="min-w-150"
            >
              <template #append-inner>
                <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
                <info>
                  The IP address (with CIDR) that will be assigned to the server.<br>
                  This address must be in the same subnet as the client addresses.
                </info>
              </template>
            </ip-field>
          </v-col>

          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.mtu"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="MTU"
                :rules="[v => Number(v) >= -1 || 'Wrong MTU.']"
                type="number"
            >
              <template #append-inner>
                <info>
                  The MTU (Maximum Transmission Unit) defines<br>
                  the largest packet size that can be sent over the network.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.fw_mark"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="FW Mark"
                :rules="[v => Number(v) >= -1 || 'Wrong FW Mark.']"
                type="number"

            >
              <template #append-inner>
                <info>
                  The firewall mark (fwmark) is an optional identifier that can be assigned to<br>
                  packets for advanced routing and filtering purposes.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.table"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="Table ID"
                :rules="[v => Number(v) >= -1 || 'Wrong Table ID.']"
                type="number"
            >
              <template #append-inner>
                <info>
                  The Table ID is an optional identifier that can be assigned to<br>
                  packets for advanced routing and filtering purposes.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.pre_up"
                density="compact"
                variant="outlined"
                label="Pre Up script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run before the interface is brought up.</info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.post_up"
                density="compact"
                variant="outlined"
                label="Post Up script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run after the interface is brought up.</info>
              </template>
            </v-textarea>
          </v-col>

          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.pre_down"
                density="compact"
                variant="outlined"
                label="Pre Down script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run before the interface is brought down.</info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.post_down"
                density="compact"
                variant="outlined"
                label="Post Down script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run after the interface is brought down.</info>
              </template>
            </v-textarea>
          </v-col>
        </block>


        <block title="Client setup" icon="mdi-account-cog-outline">
          <v-col cols="auto" md="2">
            <v-text-field
                v-model="selected.public_endpoint"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="Public Endpoint"
                :rules="[v => !!v || 'Public endpoint is required']"
                default-value="default"
                :counter="$apiStore.getMaxLength('InterfaceUpdate', 'public_endpoint')"
            >
              <template #append-inner>
                <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
                <info>
                  The public IP or DNS name of the WireGuard server will be deployed into the client's configuration.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2">
            <v-text-field
                v-model="selected.listen_port"
                density="compact"
                variant="outlined"
                class="min-w-200"
                label="Listen Port"
                :rules="[v => Number(v) >= -1 || 'Wrong port.']"
                type="number"
            >
              <template #append-inner>
                <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
                <info>
                  The port of the WireGuard server will be deployed into the client's configuration.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2">
            <v-textarea
                v-model="selected.client_allowed_ips"
                density="compact"
                variant="outlined"
                label="Client Allowed IPs"
                rows="1"
                max-rows="5"
                auto-grow
                :rules="[v => !!v || 'Client Allowed IPs are required']"
            >
              <template #append-inner>
                <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
                <info>Client Allowed IPs for this network.</info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.ip_range"
                density="compact"
                variant="outlined"
                label="IP range"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>IP ranges for this network (separated by commas or new lines).
                    <br>e.g. <pre>192.168.1.10 - 192.168.1.130<br>192.168.1.200 - 192.168.1.250</pre></info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.client_persistent_keepalive"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="Client Persistent Keepalive (sec)"
                :rules="[v => Number(v) >= -1 || 'Wrong Client Persistent Keepalive.']"
                type="number"
            >
              <template #append-inner>
                <info>
                  The Client Persistent Keepalive is an optional setting that can be used to<br>
                  keep the connection alive by sending periodic keepalive packets.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-textarea
                v-model="selected.client_dns"
                density="compact"
                variant="outlined"
                label="Client DNS"
                rows="1"
                max-rows="5"
                auto-grow
            >
              <template #append-inner>
                <info>
                  The Client DNS (Domain Name System) is used to resolve hostnames<br>
                  to IP addresses for the client.
                </info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.client_mtu"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="MTU"
                :rules="[v => Number(v) >= -1 || 'Wrong Client MTU.']"
                type="number"
            >
              <template #append-inner>
                <info>
                  The Client MTU (Maximum Transmission Unit) defines the largest<br>
                  packet size that can be sent over the network.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.client_fw_mark"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="FW Mark"
                :rules="[v => Number(v) >= -1 || 'Wrong Client FW Mark.']"
                type="number"

            >
              <template #append-inner>
                <info>
                  The client firewall mark (fwmark) is an optional identifier that can be <br>
                  assigned to packets for advanced routing and filtering purposes.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="2" v-if="fullsize">
            <v-text-field
                v-model="selected.client_table"
                density="compact"
                variant="outlined"
                class="min-w-150"
                label="Table ID"
                :rules="[v => Number(v) >= -1 || 'Wrong Table ID.']"
                type="number"
            >
              <template #append-inner>
                <info>
                  The Client table ID is an optional identifier that can be assigned<br>
                  to packets for advanced routing and filtering purposes.
                </info>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.client_pre_up"
                density="compact"
                variant="outlined"
                label="Pre Up script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run on the client before the interface is brought up.</info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.client_post_up"
                density="compact"
                variant="outlined"
                label="Post Up script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run on the client after the interface is brought up.</info>
              </template>
            </v-textarea>
          </v-col>

          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.client_pre_down"
                density="compact"
                variant="outlined"
                label="Pre Down script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run on the client before the interface is brought down.</info>
              </template>
            </v-textarea>
          </v-col>
          <v-col cols="auto" md="3" v-if="fullsize">
            <v-textarea
                v-model="selected.client_post_down"
                density="compact"
                variant="outlined"
                label="Post Down script"
                rows="1"
                max-rows="10"
                auto-grow
            >
              <template #append-inner>
                <info>The script to run on the client after the interface is brought down.</info>
              </template>
            </v-textarea>
          </v-col>
        </block>
        <v-row>
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