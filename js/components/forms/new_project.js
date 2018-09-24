import FormMixin from '../../mixins/form'
import textinput from '../text_input'

const createEnvironment = (name) => ({ name })

export default {
  name: 'new-project',

  mixins: [FormMixin],

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
      environment_names,
      name,
    } = this.initialData

    const environments = (
      environment_names.length > 0
      ? environment_names
      : [""]
    ).map(createEnvironment)

    return {
      showError: false,
      environments,
      name,
    }
  },

  mounted: function () {
    this.$root.$on('onEnvironmentAdded', this.addEnvironment)
  },

  updated: function() {
    if (this.environmentsHaveNames()) {
      this.showError = false
    }
  },

  methods: {
    addEnvironment: function (event) {
      this.environments.push(createEnvironment(""))
    },

    removeEnvironment: function (index) {
      if (this.environments.length > 1) {
        this.environments.splice(index, 1)
      }
    },

    environmentsHaveNames: function () {
      return this.environments.every((e) => e.name !== "")
    },

    validateAndOpenModal: function (modalName) {
      const textInputs = this.$children.reduce((previous, newVal) => {
        // display textInput error if it is not valid
        if (!newVal.showValid) {
          newVal.showError = true
        }

        return newVal.showValid && previous
      }, true)

      const isValid = textInputs && this.environmentsHaveNames()

      if (isValid) {
        this.openModal(modalName)
      } else {
        this.showError = true
      }
    }
  }
}
