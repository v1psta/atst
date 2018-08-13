export default {
  name: 'optionsinput',

  props: {
    name: String
  },

  methods: {
    onInput: function (e) {
      this.$root.$emit('field-change', {
        value: e.target.value,
        name: this.name
      })
    }
  }
}
