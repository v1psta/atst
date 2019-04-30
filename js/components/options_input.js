import { emitEvent } from '../lib/emitters'

export default {
  name: 'optionsinput',

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: String,
  },

  data: function() {
    const showError = (this.initialErrors && this.initialErrors.length) || false
    return {
      showError: showError,
      showValid: !showError && !!this.initialValue,
      validationError: this.initialErrors.join(' '),
      value: this.initialValue,
    }
  },

  methods: {
    onInput: function(e) {
      emitEvent('field-change', this, {
        value: e.target.value,
        name: this.name,
      })
      this.showError = false
      this.showValid = true
    },
  },
}
