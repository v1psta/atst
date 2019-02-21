import textinput from '../text_input'
import DateSelector from '../date_selector'
import uploadinput from '../upload_input'
import inputValidations from '../../lib/input_validations'
import FormMixin from '../../mixins/form'

const createLOA = number => ({ number })

export default {
  name: 'ko-review',

  mixins: [FormMixin],

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
    const loa_list = this.initialData['loa']
    const loas = (loa_list.length > 0 ? loa_list : ['']).map(createLOA)

    return {
      loas,
    }
  },

  mounted: function() {
    this.$root.$on('onLOAAdded', this.addLOA)
  },

  methods: {
    addLOA: function(event) {
      this.loas.push(createLOA(''))
    },
  },
}
