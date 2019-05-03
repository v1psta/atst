import FormMixin from '../mixins/form'
import textinput from './text_input'

export default {
  name: 'toggler',

  mixins: [FormMixin],

  props: {
    initialSelectedSection: String,
  },

  components: {
    textinput,
  },

  data: function() {
    return {
      selectedSection: this.initialSelectedSection,
      invalid: true,
      fields: {},
    }
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleChange)
  },

  methods: {
    handleFieldMount: function(event) {
      const { name, optional } = event
      this.fields[name] = optional
    },

    handleChange: function(event) {
      const { name, valid, parent_uid } = event
      this.fields[name] = valid
      this.validateForm()
    },

    validateForm: function() {
      const valid = !Object.values(this.fields).some(field => field === false)
      this.invalid = !valid
      return valid
    },

    toggleSection: function(sectionName) {
      if (this.selectedSection === sectionName) {
        this.selectedSection = null
      } else {
        this.selectedSection = sectionName
      }
    },

    handleSubmit: function(event) {
      if (this.invalid) {
        event.preventDefault()
      }
    },
  },
}
