import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'

import optionsinput from './components/options_input'
import textinput from './components/text_input'

const app = new Vue({
  el: '#app-root',
  components: {
    optionsinput,
    textinput,
  },
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
        pendingFinancialVerification: false,
        pendingCCPOApproval: false,
      }
    }
  },
  mounted: function() {
    const modalOpen = document.querySelector("#modalOpen");
    if (modalOpen) {
      const modal = modalOpen.getAttribute("data-modal");
      this.modals[modal] = true;
    }
  }
})
