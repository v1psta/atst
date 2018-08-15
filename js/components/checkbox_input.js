export default {
  name: 'checkboxinput',

  props: {
    name: String,
  },

  methods: {
    onInput: function (e) {
        console.log(e)
      this.$root.$emit('field-change', {
        value: e.target.checked,
        name: this.name
      })
    }
  }
}
