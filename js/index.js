import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'

import optionsinput from './components/options_input'
import textinput from './components/text_input'
import checkboxinput from './components/checkbox_input'
import DetailsOfUse from './components/forms/details_of_use'
import poc from './components/forms/poc'
import financial from './components/forms/financial'
import NewProject from './components/forms/new_project'

Vue.use(VTooltip)


const app = new Vue({
  el: '#app-root',
  components: {
    optionsinput,
    textinput,
    checkboxinput,
    DetailsOfUse,
    poc,
    financial,
    NewProject
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
  },
  delimiters: ['!{', '}']
})
