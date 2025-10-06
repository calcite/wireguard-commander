<script>
import {defineComponent} from "vue";
import Page from "@/components/page.vue";
import NetworkForm from './forms/networkForm.vue'
import Table from "@/components/table.vue";


export default defineComponent({
  components: {Page, Table, NetworkForm},
  props: {
    navigationDrawerWidthPx: {
      type: String,
    }
  },
  data() {
    return {
      selected: null,
      selectedEvent: null,
      gridApi: null,
      columnDefs: [
        {headerName: 'ID', field: 'id', maxWidth: 75, hide: true},
        {headerName: 'Server Name', field: 'server_name', sortIndex: 1},
        {headerName: 'Public Endpoint', field: 'public_endpoint', sortIndex: 1},
        {headerName: 'Port', field: 'listen_port', maxWidth: 100},
        {headerName: 'Interface Name', field: 'interface_name', sortIndex: 1},
        {headerName: 'Address', field: 'address'},
        {
          headerName: 'User groups',
          field: 'user_groups',
          cellRenderer: 'ChipsRenderer',
          sortable: false,
          filter: false,
        },
      ],
      rowData: null,
      defaultColDef: {
        sortable: true,
        filter: true,
        flex: 1,
        minWidth: 60
      },
      detailFullsize: false,
    }
  },
  computed: {
    isDetailShown: {
      get() {
        return this.selected !== null;;
      },
      set(value) {
        if (!value) {
          this.selected = null;
        }
      }
    }
  },
  methods: {
    async onGridReady(params) {
      const response = await this.$api.get('/api/interfaces/');
      this.rowData = response.data;
      this.gridApi = params.api;
    },
    async doSelect(event) {
      if (event.data?.id && this.selected?.id === event.data?.id) {
        this.selected = null;
      } else {
        this.selected = event.data;
        this.selectedEvent = event
      }
    },
    cancelDone(item) {
      this.selected = null;
    },
    updateDone(item) {
      this.gridApi.refreshCells({rowNodes: [this.selectedEvent.node]})
      this.selected = null;
    },
    createDone(item) {
      if (!this.rowData) {
        this.rowData = []
      }
      this.rowData.push(item)
      this.selected = null;
      this.$nextTick(() => {
        const rowIndex = this.rowData.length - 1;
        this.gridApi.ensureIndexVisible(rowIndex);
      });
    },
    deleteDone(item) {
      this.rowData = this.rowData.filter(row => row.id !== item.id);
      this.selected = null;
    }
  }
})
</script>

<template>
  <page v-model="isDetailShown" :detailPanelWidth="detailFullsize ? 'calc(100vw - ' + navigationDrawerWidthPx + ')' : '20vw'">
    <template #buttons>
      <v-btn @click="selected = {}">Add</v-btn>
    </template>


    <template #panel>
      <network-form :selected="selected"
                    @canceled="cancelDone"
                    @updated="updateDone"
                    @created="createDone"
                    @deleted="deleteDone"
                    @resize="detailFullsize = $event"
      />
    </template>

    <Table
        @ready="onGridReady"
        @select="doSelect"
        :columnDefs="columnDefs"
        :rowData="rowData"
    ></Table>
  </page>

</template>
