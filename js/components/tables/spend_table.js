import { set } from 'vue/dist/vue'
import { formatDollars } from '../../lib/dollars'

export default {
  name: 'spend-table',

  props: {
    applications: Object,
    portfolio: Object,
    environments: Object,
    currentMonthIndex: String,
    prevMonthIndex: String,
    twoMonthsAgoIndex: String
  },

  data: function () {
    return {
      applicationsState: this.applications
    }
  },

  created: function () {
    Object.keys(this.applications).forEach(application => {
      set(this.applicationsState[application], 'isVisible', false)
    })
  },

  methods: {
    toggle: function (e, applicationName) {
      this.applicationsState = Object.assign(this.applicationsState, {
        [applicationName]: Object.assign(this.applicationsState[applicationName],{
          isVisible: !this.applicationsState[applicationName].isVisible
        })
      })
    },

    formatDollars: function (value) {
      return formatDollars(value, false)
    },

    round: function (value) {
      return Math.round(value)
    }
  }
}
