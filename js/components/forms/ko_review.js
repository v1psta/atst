import textinput from '../text_input'
import DateSelector from '../date_selector'
import uploadinput from '../upload_input'
import inputValidations from '../../lib/input_validations'

const createLOA = number => ({ number })

export default {
  name: 'ko-review',

  components: {
    textinput,
    DateSelector,
    uploadinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({}),
    },
    modalName: String,
  },

  data: function() {
    const { loa } = this.initialData
    const loas =
      typeof loa === 'array' && loa.length > 0 ? this.initialValue : ['']

    return {
      loas,
    }
  },

  methods: {
    addLOA: function(event) {
      this.loas.push(createLOA(''))
    },
  },
}
