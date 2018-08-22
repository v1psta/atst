import textinput from '../text_input'

const createEnvironment = (name) => ({ name })

export default {
  name: 'new-project',

  components: {
    textinput
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({})
    }
  },

  data: function () {
    const {
      name,
      description,
      environments = [ createEnvironment() ]
    } = this.initialData

    return {
      name,
      description,
      environments,
    }
  },

  mounted: function () {
    this.$root.$on('onEnvironmentAdded', this.addEnvironment)
  },

  methods: {
    addEnvironment: function (event) {
      this.environments.push(createEnvironment(""))
    },

    removeEnvironment: function (index) {
      if (this.environments.length > 1) {
        this.environments.splice(index, 1)
      }
    }
  }
}
