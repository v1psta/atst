import { emitEvent } from '../lib/emitters'
import FormMixin from '../mixins/form'

export default {
  name: 'optionsinput',

  mixins: [FormMixin],

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: String,
    watch: {
      type: Boolean,
      default: false,
    },
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
        watch: this.watch,
      })
      this.showError = false
      this.showValid = true
    },
  },
}
