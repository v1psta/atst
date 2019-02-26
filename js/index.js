import 'svg-innerhtml'
import 'babel-polyfill'
import ally from 'ally.js'

import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'

import levelofwarrant from './components/levelofwarrant'
import optionsinput from './components/options_input'
import multicheckboxinput from './components/multi_checkbox_input'
import textinput from './components/text_input'
import checkboxinput from './components/checkbox_input'
import EditOfficerForm from './components/forms/edit_officer_form'
import poc from './components/forms/poc'
import oversight from './components/forms/oversight'
import toggler from './components/toggler'
import NewApplication from './components/forms/new_application'
import EditEnvironmentRole from './components/forms/edit_environment_role'
import EditApplicationRoles from './components/forms/edit_application_roles'
import funding from './components/forms/funding'
import uploadinput from './components/upload_input'
import Modal from './mixins/modal'
import selector from './components/selector'
import BudgetChart from './components/charts/budget_chart'
import SpendTable from './components/tables/spend_table'
import TaskOrderList from './components/tables/task_order_list.js'
import MembersList from './components/members_list'
import LocalDatetime from './components/local_datetime'
import ConfirmationPopover from './components/confirmation_popover'
import { isNotInVerticalViewport } from './lib/viewport'
import DateSelector from './components/date_selector'
import SidenavToggler from './components/sidenav_toggler'

Vue.config.productionTip = false

Vue.use(VTooltip)

Vue.mixin(Modal)

const app = new Vue({
  el: '#app-root',
  components: {
    toggler,
    levelofwarrant,
    optionsinput,
    multicheckboxinput,
    textinput,
    checkboxinput,
    poc,
    oversight,
    NewApplication,
    selector,
    BudgetChart,
    SpendTable,
    TaskOrderList,
    MembersList,
    LocalDatetime,
    EditEnvironmentRole,
    EditApplicationRoles,
    ConfirmationPopover,
    funding,
    uploadinput,
    DateSelector,
    EditOfficerForm,
    SidenavToggler,
  },

  mounted: function() {
    this.$on('modalOpen', isOpen => {
      if (isOpen) {
        document.body.className += ' modal-open'
      } else {
        document.body.className = document.body.className.replace(
          ' modal-open',
          ''
        )
      }
    })

    const modalOpen = document.querySelector('#modalOpen')

    if (modalOpen) {
      const modal = modalOpen.getAttribute('data-modal')
      this.openModal(modal)
    }

    ally.query.focusable().forEach(function(el) {
      el.addEventListener('focus', function() {
        if (isNotInVerticalViewport(el)) {
          el.scrollIntoView({ block: 'center' })
        }
      })
    })
  },
  delimiters: ['!{', '}'],
})
