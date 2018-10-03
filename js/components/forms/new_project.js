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
      validations: [
        {func: this.hasEnvironments, message: "Provide at least one environment name."},
        {func: this.envNamesAreUnique, message: "Environment names must be unique."},
        {func: this.environmentsHaveNames, message: "Environment names cannot be empty."},
      ],
      errors: [],
      environments,
      name,
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
    },

    validate: function() {
      this.errors = this.validations.map((validation) => {
        if (!validation.func()) {
          return validation.message
        }
      }).filter(Boolean)
    },

    hasEnvironments: function () {
      return this.environments.length > 0 && this.environments.some((e) => e.name !== "")
    },

    environmentsHaveNames: function () {
      if (this.environments.length > 1) {
        // only want to display this error if we have multiple envs and one or
        // more do not have names
        return this.environments.every((e) => e.name !== "")
      } else {
        return true
      }
    },

    envNamesAreUnique: function () {
      const names = this.environments.map((e) => e.name)
      return names.every((n, index) => names.indexOf(n) === index)
    },

    handleSubmit: function (modalName, event) {
      if (!this.readyToSubmit) {
        event.preventDefault()
        this.validateAndOpenModal(modalName)
      }
    },

    validateAndOpenModal: function (modalName) {
      let isValid = this.$children.reduce((previous, newVal) => {
        // display textInput error if it is not valid
        if (!newVal.showValid) {
          newVal.showError = true
        }

        return newVal.showValid && previous
      }, true)

      this.validate()
      isValid = this.errors.length == 0 && isValid

      if (isValid) {
        this.openModal(modalName)
      }
    }
  }
}
