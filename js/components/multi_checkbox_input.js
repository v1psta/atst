import optionsinput from '../components/options_input'
import textinput from '../components/text_input'
import { emitFieldChange } from '../lib/emitters'

export default {
  name: 'multicheckboxinput',

  components: {
    optionsinput,
    textinput,
  },

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
      emitFieldChange(this, { value: e.target.value, name: this.name })
      this.showError = false
      this.showValid = true
    },
    otherToggle: function() {
      this.otherChecked = !this.otherChecked
    },
  },
}
