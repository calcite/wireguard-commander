<script>
import {defineComponent} from "vue";
import Page from "@/components/page.vue";
import Table from "@/components/table.vue";


export default defineComponent({
  components: {Page, Table},
  props: {},
  data() {
    return {
      selected: null,
      selectedEvent: null,
      gridApi: null,
      rowData: null,
      columnDefs: [
        {headerName: 'ID', field: 'id', hide: true},
        {
          headerName: 'Name',
          field: 'name',
          comparator: (valueA, valueB) => {
            return getLastName(valueA).localeCompare(getLastName(valueB));
          }},
        {headerName: 'Email', field: 'email'},
        {
          headerName: 'Logged',
          field: 'last_logged_at',
          valueFormatter: (params) => {
            return params.value ? formatDate(params.value) : '';
          }, maxWidth: 200
        },
        {headerName: 'Admin', field: 'is_admin', maxWidth: 100,},
        {
          headerName: 'User groups',
          field: 'member_of_static',
          cellRenderer: 'ChipsRenderer',
          sortable: false,
          filter: false,
          valueGetter: (params) => {
            return [].concat(params.data.member_of_static, params.data.member_of_dynamic)
          }},
      ],
    }
  },
  computed: {
    isDetailShown: {
      get() {
        return this.selected !== null;
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
      // const response = await this.$api.get('/api/users/');
      this.rowData =  {} //response.data;
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
    deleteDone(item) {
      this.rowData.splice(this.selectedEvent.rowIndex, 1)
      this.gridApi.refreshCells({rowNodes: [this.selectedEvent.node]})
      this.selected = null;
    }
  }
})
</script>

<template>
  <page v-model="isDetailShown">

    <template #panel>
      <user-form :selected="selected"
                 @canceled="cancelDone"
                 @updated="updateDone"
                 @deleted="deleteDone"
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

