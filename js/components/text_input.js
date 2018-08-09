import MaskedInput, { conformToMask } from 'vue-text-mask'
import inputValidations from '../lib/input_validations'

export default {
  name: 'textinput',

  components: {
    MaskedInput
  },

  props: {
    name: String,
    validation: {
      type: String,
      default: () => 'anything'
    },
    setValue: {
      type: String,
      default: () => ''
    }
  },

  data: function () {
    return {
      showError: false,
      showValid: false,
      mask: inputValidations[this.validation].mask,
      pipe: inputValidations[this.validation].pipe || undefined,
      keepCharPositions: inputValidations[this.validation].keepCharPositions || false,
      value: this.setValue
    }
  },

  mounted: function () {
    if (this.value && this.mask) {
      this._checkIfValid({ value: this.value, invalidate: true })
      this.value = conformToMask(this.value, this.mask).conformedValue
    }
  },

  methods: {
    // When user types a character
    onInput: function (e) {
      // When we use the native textarea element, we receive an event object
      // When we use the masked-input component, we receive the value directly
      const value = typeof e === 'object' ? e.target.value : e
      this.value = value
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
      this.showValid = valid

      // Emit a change event
      this.$emit('fieldChange', {
        value,
        valid,
        name: this.name
      })
    },

    _rawValue: function (value) {
      return inputValidations[this.validation].unmask.reduce((currentValue, character) => {
        return currentValue.split(character).join('')
      }, value)
    },

    _validate: function (value) {
      return inputValidations[this.validation].match.test(this._rawValue(value))
    }
  }
}
