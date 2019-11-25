import { emitFieldChange } from '../lib/emitters'

export default {
  name: 'multicheckboxinput',

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: {
      type: Array,
      default: () => [],
    },
    initialOtherValue: String,
    optional: Boolean,
  },

  data: function() {
    const showError = (this.initialErrors && this.initialErrors.length) || false
    return {
      showError: showError,
      showValid: !showError && this.initialValue.length > 0,
      validationError: this.initialErrors.join(' '),
      otherChecked: this.initialValue.includes('other')
        ? true
        : this.otherChecked,
      otherText: this.initialValue.includes('other')
        ? this.initialOtherValue
        : '',
      selections: this.initialValue,
    }
  },

  methods: {
    onInput: function(e) {
      emitFieldChange(this)
      this.showError = false
      this.showValid = true
    },
    otherToggle: function() {
      this.otherChecked = !this.otherChecked
    },
  },

  computed: {
    valid: function() {
      return this.optional || this.showValid
    },
  },
}
