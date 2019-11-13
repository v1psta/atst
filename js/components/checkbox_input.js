export default {
  name: 'checkboxinput',

  props: {
    name: String,
    initialChecked: Boolean,
    optional: Boolean,
  },

  data: function() {
    return {
      isChecked: this.initialChecked,
    }
  },

  methods: {
    onInput: function() {
      this.$parent.$emit('field-change')
    },
  },

  computed: {
    valid: function() {
      return this.optional || this.isChecked
    },
  },
}
