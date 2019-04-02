import savebutton from '../components/save_button'

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
          this.disabled = false
        }
      }
    },
  },

  data: function() {
    return {
      disabled: this.disableSave,
    }
  },

  props: {
    disableSave: {
      type: Boolean,
      default: true,
    },
  },

  components: {
    savebutton,
  },
}
