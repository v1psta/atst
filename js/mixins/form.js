export default {
  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  methods: {
    handleFieldChange: function(event) {
      const { value, name } = event
      if (typeof this[name] !== undefined) {
        this[name] = value
        if (event['parent_uid'] === this._uid) {
          this.changed = true
        }
      }
    },
  },

  data: function() {
    return {
      changed: this.hasChanges,
    }
  },

  props: {
    hasChanges: {
      type: Boolean,
      default: false,
    },
  },
}
