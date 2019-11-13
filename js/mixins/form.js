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

  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
    this.$on('field-change', this.handleFieldChange)
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
    this.$on('field-mount', this.handleFieldMount)
  },

  methods: {
    handleFieldChange: function(event) {
      const { value, name, valid, parent_uid, watch } = event
      if (typeof this.fields[name] !== undefined) {
        this.fields[name] = valid
        if (parent_uid === this._uid || watch) {
          this.changed = true
        }
      }

      this.validateForm()
    },

    handleChildFieldChange: function(event) {
      // need to temporarily use this function because we will no longer be passing
      // parent_uid or watch from the child components
      const { name, valid } = event
      if (typeof this.fields[name] !== 'undefined') {
        this.fields[name] = valid
        this.changed = true
      }

      this.validateForm()
    },

    handleFieldMount: function(event) {
      const { name, optional, valid } = event
      this.fields[name] = optional || valid
      const formValid = this.validateForm()
      this.invalid = !formValid
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

  computed: {
    canSave: function() {
      const formValid = !this.invalid

      if (this.changed && formValid) {
        return true
      } else if (this.enableSave && formValid) {
        return true
      } else {
        return false
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
}
