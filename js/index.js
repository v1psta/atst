import 'svg-innerhtml'
import 'babel-polyfill'

import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'

import optionsinput from './components/options_input'
import multicheckboxinput from './components/multi_checkbox_input'
import otherinput from './components/other_input'
import textinput from './components/text_input'
import checkboxinput from './components/checkbox_input'
import DetailsOfUse from './components/forms/details_of_use'
import poc from './components/forms/poc'
import financial from './components/forms/financial'
import toggler from './components/toggler'
import NewProject from './components/forms/new_project'
import EditEnvironmentRole from './components/forms/edit_environment_role'
import EditProjectRoles from './components/forms/edit_project_roles'
import Modal from './mixins/modal'
import selector from './components/selector'
import BudgetChart from './components/charts/budget_chart'
import SpendTable from './components/tables/spend_table'
import CcpoApproval from './components/forms/ccpo_approval'
import MembersList from './components/members_list'
import LocalDatetime from './components/local_datetime'
import RequestsList from './components/requests_list'
import ConfirmationPopover from './components/confirmation_popover'

Vue.config.productionTip = false

Vue.use(VTooltip)

Vue.mixin(Modal)

const app = new Vue({
  el: '#app-root',
  components: {
    toggler,
    optionsinput,
    multicheckboxinput,
    otherinput,
    textinput,
    checkboxinput,
    DetailsOfUse,
    poc,
    financial,
    NewProject,
    selector,
    BudgetChart,
    SpendTable,
    CcpoApproval,
    MembersList,
    LocalDatetime,
    EditEnvironmentRole,
    EditProjectRoles,
    RequestsList,
    ConfirmationPopover,
  },

  mounted: function() {
    this.$on('modalOpen', isOpen => {
      if (isOpen) {
        document.body.className += ' modal-open'
      } else {
        document.body.className = document.body.className.replace(' modal-open', '')
      }
    })

    const modalOpen = document.querySelector("#modalOpen")

    if (modalOpen) {
      const modal = modalOpen.getAttribute("data-modal")
      this.openModal(modal)
    }
  },
  delimiters: ['!{', '}']
})
