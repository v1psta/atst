import optionsinput from '../components/options_input'
import textinput from '../components/text_input'

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
      default: () => []
    },
    initialValue: {
      type: Array,
      default: () => []
    },
    initialOtherValue: String,
  },


  data: function () {
    const showError = (this.initialErrors && this.initialValue.length > 0) || false
    return {
      showError: showError,
      showValid: !showError && !!this.initialValue,
      validationError: this.initialErrors.join(' '),
      otherChecked: this.initialValue.includes("other") ? true : this.otherChecked,
      otherText: this.initialOtherValue,
      selections: this.setSelection()
    }
  },

  methods: {
    onInput: function (e) {
      this.$root.$emit('field-change', {
        value: e.target.value,
        name: this.name
      })
      this.showError = false
      this.showValid = true
    },
    otherToggle: function() {
      this.otherChecked = !this.otherChecked
      this.otherText = ''
    },
    setSelection: function () {
      for (let choice of this.initialValue) {
        this.selections.push(choice)
      }
    }
  }
}
