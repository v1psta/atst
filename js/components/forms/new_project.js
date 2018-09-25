import FormMixin from '../../mixins/form'
import textinput from '../text_input'

const createEnvironment = (name) => ({ name })

const VALIDATIONS = {
  showMissingError: "hasEnvironments",
  showUniqueError: "envNamesAreUnique",
  showEmptyError: "environmentsHaveNames",
}

class Validator {
  constructor(validations) {
    this.validations = validations
  }

  errorList() {
    let errors = {}
    this.map((key) => {
      errors[key] = false
    })
    return errors
  }

  map(callback) {
    Object.keys(this.validations).map((k) => callback(k))
  }

  update(object) {
    this.map((errName) => {
      if (object[this.validations[errName]]()) {
        object.errors[errName] = false
      }
    })
  }

  validate(object) {
    this.map((errName) => {
      object.errors[errName] = !object[this.validations[errName]]()
    })
    return Object.values(object.errors).every(e => e)
  }
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

    const validator = new Validator(VALIDATIONS)

    return {
      validator,
      errors: validator.errorList(),
      environments,
      name,
    }
  },

  mounted: function () {
    this.$root.$on('onEnvironmentAdded', this.addEnvironment)
  },

  updated: function() {
    this.validator.update(this)
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

      isValid = this.validator.validate(this) && isValid

      if (isValid) {
        this.openModal(modalName)
      }
    }
  }
}
