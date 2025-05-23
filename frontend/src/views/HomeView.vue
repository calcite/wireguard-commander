<script>
import {defineComponent} from "vue";


export default defineComponent({
  components: {},
  data() {
    return {

    }
  },
  async beforeMount() {

  },
  methods: {
    open(ip) {

    }
  }
})
</script>

<template>
  <v-card flat>
    <template v-slot:title>
      <span class="text-h4"><v-icon icon="mdi-login" class="mr-3" style="font-size: 0.9em" />Login</span>
    </template>
    <template v-slot:subtitle>
      <span class="pl-16">Login</span>
    </template>
    <v-card-text>
      <v-divider theme="dark" class="mb-8"></v-divider>
      <v-sheet class="d-flex flex-wrap text-center">
        <v-sheet class="ma-2 pa-2">
          <v-card
              style="min-width: 300px; min-height: 167px"
              title="Login"
              subtitle="Login by domain credentials."
              max-width="500"
          >
            <v-card-item>
              <v-btn prepend-icon="mdi-login"
                     color="primary"
                     @click="">
                Login
              </v-btn>
            </v-card-item>
          </v-card>
        </v-sheet>


      </v-sheet>
    </v-card-text>
  </v-card>
</template>

