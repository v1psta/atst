import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'

import TextInput from './components/text_input'

const components = {
  TextInput
}

const app = new Vue({
  el: '#app-root',
  methods: {
    closeModal: function(name) {
      this.modals[name] = false
    },
    openModal: function (name) {
      this.modals[name] = true
    }
  },
  data: function() {
    return {
      modals: {
        styleguideModal: false,
      }
    }
  },
  components: components
})
