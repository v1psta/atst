import FormMixin from '../../mixins/form'
import checkboxinput from '../checkbox_input'
import textinput from '../text_input'

export default {
  name: 'edit-officer-form',

  mixins: [FormMixin],

  components: {
    checkboxinput,
    textinput,
  },

  props: {
    hasChanges: {
      type: Boolean,
      default: () => false,
    },
    hasErrors: {
      type: Boolean,
      default: () => false,
    },
  },

  data: function() {
    return {
      editing: this.hasErrors || this.hasChanges,
    }
  },

  methods: {
    edit: function(event) {
      event.preventDefault()
      this.editing = true
    },

    cancel: function(event) {
      this.editing = false
    },
  },

  template: '<div></div>',
}
