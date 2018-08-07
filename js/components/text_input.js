import MaskedInput from 'vue-text-mask'
import inputValidations from '../lib/input_validations'

const validationTypes = {
  matchAnything: /^(?!\s*$).+/,
  matchDigits: /^\d+$/,
  matchNumbers: /^-?\d+\.?\d*$/,
  matchUrl: /^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/,
  matchEmail: /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
}

export default {
  name: 'textinput',
  data: () =>({
    valid: false,
    filled: false,
    showError: false,
    showValid: false,
    validationType: inputValidations.anything.match,
    mask: inputValidations.anything.mask
  }),
  components: {
    MaskedInput
  },
  methods: {
    // When user types a character
    onInput: function (value) {
      this._checkIfFilled(value)
      this._checkIfValid(value)
    },

    // When field is blurred (un-focused)
    onChange: function (value) {
      this._checkIfInvalid(value)
    },

    _checkIfFilled: function (value) {
      this.filled = (value && value !== '') ? true : false
    },

    _checkIfValid: function (value) {
      const valid = this._validate(value)
      if (valid) {
        this.showError = false
      }
      this.valid = valid
      this.showValid = valid
    },

    _checkIfInvalid: function (value) {
      const valid = this._validate(value)
      if (!valid) {
        this.showError = true
      } else {
        this.showError = false
      }
      this.valid = valid
      this.showValid = valid
    },

    _validate: function (value) {
      return this.validationType.test(value)
    }
  }
}
