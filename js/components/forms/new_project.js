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
      showMissingError: false,
      showUniqueError: false,
      environments,
      name,
    }
  },

  mounted: function () {
    this.$root.$on('onEnvironmentAdded', this.addEnvironment)
  },

  updated: function() {
    if (this.environmentsHaveNames()) {
      this.showMissingError = false
    }

    if (this.envNamesAreUnique()) {
      this.showUniqueError = false
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

    envNamesAreUnique: function () {
      const names = this.environments.map((e) => e.name)
      return [...new Set(names)].length == this.environments.length
    },

    validateAndOpenModal: function (modalName) {
      let isValid = this.$children.reduce((previous, newVal) => {
        // display textInput error if it is not valid
        if (!newVal.showValid) {
          newVal.showError = true
        }

        return newVal.showValid && previous
      }, true)

      if (!this.environmentsHaveNames()) {
        isValid = false
        this.showMissingError = true
      }

      if (!this.envNamesAreUnique()) {
        isValid = false
        this.showUniqueError = true
      }

      if (isValid) {
        this.openModal(modalName)
      }
    }
  }
}
