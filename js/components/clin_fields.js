import DateSelector from './date_selector'
import optionsinput from './options_input'
import textinput from './text_input'

export default {
  name: 'clin-fields',

  components: {
    textinput,
  },

  props: {
    initialClinIndex: Number,
  },

  data: function() {
    return {clinIndex: this.initialClinIndex}
  },
}
