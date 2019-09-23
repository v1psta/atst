import FormMixin from '../../../mixins/form'
import textinput from '../../text_input'
import * as R from 'ramda'

export default {
  name: 'application-name-and-description',

  mixins: [FormMixin],

  components: {
    textinput,
  },

  data: function() {
    return {
      errors: [],
    }
  },
}
