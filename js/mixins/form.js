export default {
  props: {
    initialSelectedSection: String,
    hasChanges: {
      type: Boolean,
      default: false,
    },
    enableSave: {
      type: Boolean,
      default: false,
    },
  },

  data: function() {
    return {
      changed: this.hasChanges,
      valid: false,
    }
  },

  mounted: function() {
    this.$on('field-change', this.handleFieldChange)
    this.valid = this.validateFields()
  },

  methods: {
    handleFieldChange: function(event) {
      this.valid = this.validateFields()
      this.changed = true
    },

    validateFields: function() {
      return this.$children.every(child => child.valid)
    },

    handleSubmit: function(event) {
      if (!this.valid) {
        event.preventDefault()
      }
    },
  },

  computed: {
    canSave: function() {
      if (this.changed && this.valid) {
        return true
      } else if (this.enableSave && this.valid) {
        return true
      } else {
        return false
      }
    },
  },
}
