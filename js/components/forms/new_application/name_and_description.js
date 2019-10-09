import FormMixin from '../../../mixins/form'
import textinput from '../../text_input'
import * as R from 'ramda'

export default {
  name: 'application-name-and-description',

  mixins: [FormMixin],

  components: {
    textinput,
  },
  created: function() {
    this.$root.$on('field-change', this.handleFieldChange)
    if (this.initialData) this.changed = true
  },

  data: function() {
    return {
      errors: [],
    }
  },
}
