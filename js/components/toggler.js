import editEnvironmentRole from './forms/edit_environment_role'
import FormMixin from '../mixins/form'
import optionsinput from './options_input'
import textinput from './text_input'

export default {
  name: 'toggler',

  mixins: [FormMixin],

  props: {
    initialSelectedSection: {
      type: String,
      default: null,
    },
  },

  components: {
    editEnvironmentRole,
    optionsinput,
    textinput,
    optionsinput,
  },

  data: function() {
    return {
      selectedSection: this.initialSelectedSection,
    }
  },

  methods: {
    toggleSection: function(sectionName) {
      if (this.selectedSection === sectionName) {
        this.selectedSection = null
      } else {
        this.selectedSection = sectionName
      }
    },
  },
}
