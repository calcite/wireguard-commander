<script>
import {defineComponent} from "vue";
import {AgGridVue} from "ag-grid-vue3"; // Vue Data Grid Component

import ChipsRenderer from "@/components/ChipsRender.vue";

export default defineComponent({
  emits: ['ready', 'select'],
  components: {AgGridVue},
  props: {
    columnDefs: {
      type: Object,
    },
    rowData: {},
    defaultCol: {
      type: Object,
      default: {}
    },
    getRowStyle: {
      default: null
    },
    heightOffset: {
      default: 0
    },
    statusBar: {
      default: null
    }
  },
  data() {
    return {
      defaultColDef: {
        sortable: true,
        filter: true,
        flex: 1,
        minWidth: 100
      },
      frameworkComponents: {
        ChipsRenderer
      },
    }
  },
  computed: {
    drawerHeightPx() {
      const height = this.heightOffset + 150 + (this.$vuetify.display.mobile ? 75 : 0);
      return  `${height}px`;
    },
    myDefault() {
      let res = {}
      Object.assign(res, this.defaultColDef, this.defaultCol)
      return res
    }
  },
  methods: {

  }
})
// domLayout="autoHeight"
</script>
<template>
  <div class="ag-theme-quartz wrapper" >
    <ag-grid-vue
        class="ag-theme-quartz table"
        :rowData="rowData"
        :defaultColDef="myDefault"
        :columnDefs="columnDefs"
        :animateRows="true"
        :getRowStyle="getRowStyle"
        :components="frameworkComponents"
        @grid-ready="(event) => $emit('ready', event)"
        @rowClicked="(event) => $emit('select', event)"
    />
  <div class="status-bar">
    <slot name="status-bar">
      <slot name="status-bar-pre"></slot>
      <v-spacer/>
      Total Rows: {{ rowData?.length || 0 }}
    </slot></div>
  </div>
</template>

<style scoped>
.wrapper {
  width: 100%;
  overflow-y: auto;
  margin-bottom: 50px;
}
.table {
  width: 100%;
  height: calc(100vh - v-bind(drawerHeightPx));
  position: relative;
  z-index: 100;
}
.status-bar {
  z-index: 50;
  font-family: var(--ag-font-family);
  font-size: var(--ag-font-size);
  line-height: normal;
  height: 54px;
  display: flex;
  position:relative;
  top: -4px;
  justify-content: space-between;
  align-items: center;
  border-radius: 0 0 var(--ag-border-radius) var(--ag-border-radius);
  border: var(--ag-borders) var(--ag-border-color);
  border-top: 0;
  font-weight: 400;
  background-color: var(--ag-background-color);
  color: var(--ag-header-foreground-color);
  padding-left: var(--ag-cell-horizontal-padding);
  padding-right: var(--ag-cell-horizontal-padding);
  white-space: nowrap;
}
</style>
