import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'

import optionsinput from './components/options_input'
import textinput from './components/text_input'
import checkboxinput from './components/checkbox_input'
import DetailsOfUse from './components/forms/details_of_use'
import poc from './components/forms/poc'
import financial from './components/forms/financial'
import toggler from './components/toggler'
import NewProject from './components/forms/new_project'
import Modal from './mixins/modal'

Vue.use(VTooltip)

Vue.mixin(Modal)

const app = new Vue({
  el: '#app-root',
  components: {
    toggler,
    optionsinput,
    textinput,
    checkboxinput,
    DetailsOfUse,
    poc,
    financial,
    NewProject
  },
  mounted: function() {
    const modalOpen = document.querySelector("#modalOpen")
    if (modalOpen) {
      const modal = modalOpen.getAttribute("data-modal")
      this.openModal(modal)
    }
  },
  delimiters: ['!{', '}']
})
