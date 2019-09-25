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
    optionsinput,
    textinput,
    optionsinput,
    toggler: this,
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
