import DateSelector from './date_selector'
import { emitEvent } from '../lib/emitters'
import optionsinput from './options_input'
import textinput from './text_input'

const JEDI_CLIN_TYPE = 'jedi_clin_type'
const OBLIGATED_AMOUNT = 'obligated_amount'

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
    initialClinType: String,
    initialAmount: {
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
      clinType: this.initialClinType,
      amount: this.initialAmount || 0,
    }
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  created: function() {
    emitEvent('clin-change', this, {
      id: this._uid,
      clinType: this.clinType,
      amount: this.initialAmount,
    })
  },

  methods: {
    addLoa: function(event) {
      ++this.loas
    },

    loaIndex: function(index) {
      return index + this.indexOffset - 1
    },

    clinChangeEvent: function() {
      emitEvent('clin-change', this, {
        id: this._uid,
        clinType: this.clinType,
        amount: this.amount,
      })
    },

    handleFieldChange: function(event) {
      if (this._uid === event.parent_uid) {
        if (event.name.includes(JEDI_CLIN_TYPE)) {
          this.clinType = event.value
          this.clinChangeEvent()
        } else if (event.name.includes(OBLIGATED_AMOUNT)) {
          this.amount = parseFloat(event.value)
          this.clinChangeEvent()
        }
      }
    },
  },
}
