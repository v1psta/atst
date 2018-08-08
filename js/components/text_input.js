import MaskedInput, { conformToMask } from 'vue-text-mask'
import inputValidations from '../lib/input_validations'

export default {
  name: 'textinput',

  components: {
    MaskedInput
  },

  props: {
    validation: {
      type: String,
      default: () => 'anything'
    },
    value: {
      type: String,
      default: () => ''
    }
  },

  data: function () {
    return {
      valid: false,
      showError: false,
      showValid: false,
      mask: inputValidations[this.validation].mask
    }
  },

  mounted: function () {
    const value = this.$refs.input.value
    if (value) {
      this._checkIfValid({ value, invalidate: true })
      this.value = conformToMask(value, this.mask).conformedValue
    }
  },

  methods: {
    // When user types a character
    onInput: function (value) {
      this._checkIfValid({ value })
    },

    // When field is blurred (un-focused)
    onChange: function (e) {
      // Only invalidate the field when it blurs
      this._checkIfValid({ value: e.target.value, invalidate: true })
    },

    //
    _checkIfValid: function ({ value, invalidate = false}) {
      // Validate the value
      const valid = this._validate(value)

      // Show error messages or not
      if (valid) {
        this.showError = false
      } else if (invalidate) {
        this.showError = true
      }
      this.valid = valid
      this.showValid = valid
    },

    _validate: function (value) {
      // Strip out all the mask characters
      let rawValue = inputValidations[this.validation].unmask.reduce((currentValue, character) => {
        return currentValue.split(character).join('')
      }, value)

      return inputValidations[this.validation].match.test(rawValue)
    }
  }
}
