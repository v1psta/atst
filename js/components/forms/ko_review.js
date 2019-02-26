import textinput from '../text_input'
import DateSelector from '../date_selector'
import uploadinput from '../upload_input'
import inputValidations from '../../lib/input_validations'
import FormMixin from '../../mixins/form'

const createLOA = number => ({ number })

// add in component for multi-loa-input here!

const multiLoaInput = {
  name: 'multi-loa-input',

  mixins: [FormMixin],

  props: {
    initialData: {
      type: Array,
      default: () => [],
    },
    initialErrors: {
      type: Array,
      default: () => [],
    }
  },

  data: function() {
    const loas = (this.initialData.length > 0 ? this.initialData : ['']).map(createLOA)

    return {
      showError: false,
      showValid: false,
      loas,
      loaErrors: [],
      readyToSubmit: false,
      validations: [
        {
          func: this.hasLOAs,
          message: 'Provide at least one LOA.'
        },
        {
          func: this.loasHaveNumbers,
          messge: 'An LOA cannot be empty.'
        },
        {
          func: this.loasAreUnique,
          message: 'An LOA must be unique.'
        }
      ]
    }
  },

  mounted: function() {
    this.$root.$on('onLOAAdded', this.addLOA)
  },

  methods: {
    addLOA: function(event) {
      this.loas.push(createLOA(''))
    },

    removeLOA: function(index) {
      if (this.loas.length > 1) {
        this.loas.splice(index, 1)
      }
    },

    hasLOAs: function() {
      return (
        this.loas.length > 0 && this.loas.some(loa => loa.number !== '')
      )
    },

    loasHaveNumbers: function() {
      if (this.loas.length> 1) {
        return this.loas.every(loa => loa.number !== '')
      } else {
        return true
      }
    },

    loasAreUnique: function() {
      const numbers = this.loas.map(loa => loa.number)
      return numbers.every((n, index) => numbers.indexOf(n) === index)
    },

    validate: function() {
      this.loaErrors = this.validations.map(validation => {
        if (!validation.func()) {
          return validation.message
        }
      }).filter(Boolean)

      if (this.loaErrors.length > 0) {
        this.showError = true
        this.showValid = false
      } else {
        this.showError = false
        this.showValid = true
      }
    }
  }
}


export default {
  name: 'ko-review',

  mixins: [FormMixin],

  components: {
    textinput,
    DateSelector,
    uploadinput,
    multiLoaInput
  },

  props: {
    modalName: String,
  },

  data: function() {
    return {
      readyToSubmit: false,
    }
  },

  methods: {
    validate: function() {
      let isValid = this.$children.reduce((previous, newVal) => {
        debugger
        if (newVal.$vnode.componentOptions.tag === 'multi-loa-input') {
          newVal.validate()
        }
        // check each child component to see if it is valid
        if (!newVal.showValid) {
          newVal.showError = true
        }

        return newVal.showValid && previous
      }, true)


      if(isValid) {
        this.readyToSubmit = true
      }
    },

    handleSubmit: function(event) {
      this.validate()
      if (!this.readyToSubmit) {
        event.preventDefault()
      }
    }
  },
}
