import DateSelector from './date_selector'
import optionsinput from './options_input'
import textinput from './text_input'

export default {
  name: 'clin-fields',

  components: {
    DateSelector,
    optionsinput,
    textinput,
  },

  props: {
    initialClinIndex: Number,
    initialLoaCount: {
      type: Number,
      default: 0,
    },
  },

  data: function() {
    const loas = this.initialLoaCount == 0 ? 1 : 0
    const indexOffset = this.initialLoaCount

    return {
      clinIndex: this.initialClinIndex,
      indexOffset: this.initialLoaCount,
      loas: loas,
    }
  },

  methods: {
    addLoa: function(event) {
      ++this.loas
    },

    loaIndex: function(index) {
      return index + this.indexOffset - 1
    },
  },
}
