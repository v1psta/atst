import MaskedInput, { conformToMask } from 'vue-text-mask'
import inputValidations from '../lib/input_validations'
import { formatDollars } from '../lib/dollars'
import { emitEvent } from '../lib/emitters'

export default {
  name: 'clindollaramount',

  components: {
    MaskedInput,
  },

  props: {
    name: String,
    validation: {
      type: String,
      default: () => 'clinDollars',
    },
    initialValue: {
      type: String,
      default: () => '',
    },
    initialErrors: {
      type: Array,
      default: () => [],
    },

    optional: Boolean,
    fundingValid: Boolean,
    watch: {
      type: Boolean,
      default: false,
    },
  },

  data: function() {
    return {
      showErrorState:
        (this.initialErrors && this.initialErrors.length) || false,
      showValidationState: false,
      mask: inputValidations[this.validation].mask,
      pipe: inputValidations[this.validation].pipe || undefined,
      keepCharPositions:
        inputValidations[this.validation].keepCharPositions || false,
      validationError:
        this.initialErrors.join(' ') ||
        inputValidations[this.validation].validationError,
      value: this.initialValue,
      modified: false,
    }
  },

  computed: {
    rawValue: function() {
      return this._rawValue(this.value)
    },
    showError: function() {
      return this.showErrorState || !this.fundingValid
    },
    showValid: function() {
      return this.showValidationState && this.fundingValid
    },
  },

  mounted: function() {
    if (this.value) {
      this._checkIfValid({
        value: this.value,
        invalidate: true,
        showValidationStateationIcon: false,
      })

      if (this.mask && this.validation !== 'email') {
        const mask =
          typeof this.mask.mask !== 'function'
            ? this.mask
            : mask.mask(this.value).filter(val => val !== '[]')

        this.value = conformToMask(this.value, mask).conformedValue
      }
    }
  },

  created: function() {
    emitEvent('field-mount', this, {
      optional: this.optional,
      name: this.name,
      valid: this._isValid(this.value),
    })
  },

  methods: {
    // When user types a character
    onInput: function(e) {
      // When we use the native textarea element, we receive an event object
      // When we use the masked-input component, we receive the value directly
      const value = typeof e === 'object' ? e.target.value : e
      this.value = value
      this.modified = true
      this._checkIfValid({ value })
    },

    // When field is blurred (un-focused)
    onChange: function(e) {
      // Only invalidate the field when it blurs
      this._checkIfValid({ value: e.target.value, invalidate: true })
    },

    onBlur: function(e) {
      if (!(this.optional && e.target.value === '')) {
        this._checkIfValid({ value: e.target.value.trim(), invalidate: true })
      } else if (this.modified && !this.optional) {
        this._checkIfValid({ value: e.target.value.trim(), invalidate: true })
      }
      this.value = e.target.value.trim()
      let value = Number.isNaN(e.target.value) ? '0' : e.target.value
      this.value = formatDollars(this._rawValue(value))
    },

    _checkIfValid: function({
      value,
      invalidate = false,
      showValidationStateationIcon = true,
    }) {
      const valid = this._isValid(value)
      if (this.modified) {
        this.validationError = inputValidations[this.validation].validationError
      }

      // Show error messages or not
      if (valid) {
        this.showErrorState = false
      } else if (invalidate) {
        this.showErrorState = true
      }

      if (showValidationStateationIcon) {
        this.showValidationState = this.value != '' && valid
      }

      // Emit a change event
      emitEvent('field-change', this, {
        value: this._rawValue(value),
        valid: this._isValid(value),
        name: this.name,
        watch: this.watch,
      })
    },

    _rawValue: function(value) {
      return inputValidations[this.validation].unmask.reduce(
        (currentValue, character) => {
          return currentValue.split(character).join('')
        },
        value
      )
    },

    _validate: function(value) {
      const rawValue = this._rawValue(value)
      if (rawValue < 0 || rawValue > 1000000000 || !this.fundingValid) {
        return false
      }
      return inputValidations[this.validation].match.test(rawValue)
    },

    _isValid: function(value) {
      let valid = this._validate(value)
      if (!this.modified && this.initialErrors && this.initialErrors.length) {
        valid = false
      } else if (this.optional && value === '') {
        valid = true
      } else if (!this.optional && value === '') {
        valid = false
      }

      return valid
    },
  },
}
