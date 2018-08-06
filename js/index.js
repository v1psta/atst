import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'

const app = new Vue({
  el: '#vue-root',
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
  }
})

console.log('hello from index')
