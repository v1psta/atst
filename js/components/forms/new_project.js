import FormMixin from '../../mixins/form'
import textinput from '../text_input'

const createEnvironment = (name) => ({ name })

const VALIDATIONS = {
  showMissingError: "hasEnvironments",
  showUniqueError: "envNamesAreUnique",
  showEmptyError: "environmentsHaveNames",
}

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

    let errors = {}
    Object.keys(VALIDATIONS).map((key) => {
      errors[key] = false
    })

    return {
      errors,
      environments,
      name,
    }
  },

  mounted: function () {
    this.$root.$on('onEnvironmentAdded', this.addEnvironment)
  },

  updated: function() {
    Object.keys(VALIDATIONS).map((errName) => {
      const func = VALIDATIONS[errName]
      if (this[func]()) {
        this.errors[errName] = false
      }
    })
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

      Object.keys(VALIDATIONS).map((errName) => {
        const func = VALIDATIONS[errName]
        if (!this[func]()) {
          isValid = false
          this.errors[errName] = true
        }
      })

      if (isValid) {
        this.openModal(modalName)
      }
    }
  }
}
