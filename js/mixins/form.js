export default {
  props: {
    initialSelectedSection: String,
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
  },

  methods: {
    handleFieldChange: function(event) {
      const { name, valid, parent_uid } = event
      if (typeof this[name] !== undefined) {
        this.fields[name] = valid

        if (parent_uid === this._uid) {
          this.changed = true
        }
      }

      this.validateForm()
    },

    handleFieldMount: function(event) {
      const { name, optional } = event
      this.fields[name] = optional
    },

    validateForm: function() {
      const valid = !Object.values(this.fields).some(field => field === false)
      this.invalid = !valid
      return valid
    },

    handleSubmit: function(event) {
      if (this.invalid) {
        event.preventDefault()
      }
    },
  },

  data: function() {
    return {
      changed: this.hasChanges,
      fields: {},
      invalid: true,
    }
  },

  props: {
    hasChanges: {
      type: Boolean,
      default: false,
    },
  },
}
