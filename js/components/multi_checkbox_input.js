import otherinput from '../components/other_input'
import optionsinput from '../components/options_input'
import textinput from '../components/text_input'

export default {
  name: 'multicheckboxinput',

  components: {
    otherinput,
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
    }
  },


  data: function () {
    const showError = (this.initialErrors && this.initialErrors.length) || false
    return {
      showError: showError,
      showValid: !showError && !!this.initialValue,
      validationError: this.initialErrors.join(' '),
      otherChecked: this.initialValue.includes("other") ? true : this.otherChecked
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
    }
  }
}
