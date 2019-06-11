import checkboxinput from './checkbox_input'

export default {
  name: 'submit-confirmation',

  components: {
    checkboxinput,
  },

  data: function() {
    return {
      valid: false,
    }
  },

  methods: {
    toggleValid: function() {
      this.valid = !this.valid
    },
  },
}
