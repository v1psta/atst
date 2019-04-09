import { set } from 'vue/dist/vue'

export default {
  name: 'environments-table',

  props: {
    environments: Object,
  },

  data: function() {
    return {
      environmentsState: this.environments,
    }
  },

  created: function() {
    Object.keys(this.environments).forEach(environment => {
      set(this.environmentsState[environment], 'isVisible', false)
    })
  },

  methods: {
    toggle: function(e, environmentName) {
      this.environmentsState = Object.assign(this.environmentsState, {
        [environmentName]: Object.assign(
          this.environmentsState[environmentName],
          {
            isVisible: !this.environmentsState[environmentName].isVisible,
          }
        ),
      })
    },
  },
}
