import checkboxinput from './checkbox_input'

export default {
  name: 'submit-confirmation',

  components: {
    checkboxinput,
  },

  data: function() {
    return {
      valid: false,
      checked: false,
    }
  },

  methods: {
    toggleValid: function() {
      this.valid = !this.valid
    },

    handleClose: function() {
      this.$root.closeModal(this.name)
      this.checked = false
      this.valid = false
    },
  },
}
