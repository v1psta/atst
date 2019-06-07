import DateSelector from './date_selector'
import textinput from './text_input'

export default {
  name: 'clin-fields',

  components: {
    DateSelector,
    textinput,
  },

  props: {
    initialClinIndex: Number,
  },

  data: function() {
    return {clinIndex: this.initialClinIndex}
  },
}
