export default {
  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  methods: {
    handleFieldChange: function(event) {
      const { value, name } = event
      if (typeof this[name] !== undefined) {
        this[name] = value
      }
    },
  },
}
