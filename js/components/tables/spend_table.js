import { set } from 'vue/dist/vue'
import { formatDollars } from '../../lib/dollars'

export default {
  name: 'spend-table',

  props: {
    projects: Object,
    workspace: Object,
    environments: Object,
    currentMonthIndex: String,
    prevMonthIndex: String,
    twoMonthsAgoIndex: String
  },

  data: function () {
    return {
      projectsState: this.projects
    }
  },

  created: function () {
    Object.keys(this.projects).forEach(project => {
      set(this.projectsState[project], 'isVisible', false)
    })
  },

  methods: {
    toggle: function (e, projectName) {
      this.projectsState = Object.assign(this.projectsState, {
        [projectName]: {
          isVisible: !this.projectsState[projectName].isVisible
        }
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
