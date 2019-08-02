import DateSelector from './date_selector'
import { emitEvent } from '../lib/emitters'
import optionsinput from './options_input'
import textinput from './text_input'

const JEDI_CLIN_TYPE = 'jedi_clin_type'
const OBLIGATED_AMOUNT = 'obligated_amount'
const START_DATE = 'start_date'
const END_DATE = 'end_date'
const POP = 'period_of_performance'

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
    initialStartDate: {
      type: String,
      default: null,
    },
    initialEndDate: {
      type: String,
      default: null,
    },
  },

  data: function() {
    const loas = this.initialLoaCount == 0 ? 1 : 0
    const indexOffset = this.initialLoaCount
    const start = new Date(this.initialStartDate)
    const end = new Date(this.initialEndDate)
    const popValidation = !this.initialStartDate ? false : start < end
    const showPopValidation = !this.initialStartDate ? false : !popValidation

    return {
      clinIndex: this.initialClinIndex,
      indexOffset: this.initialLoaCount,
      loas: loas,
      clinType: this.initialClinType,
      amount: this.initialAmount || 0,
      startDate: start,
      endDate: end,
      popValid: popValidation,
      showPopError: showPopValidation,
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
    emitEvent('field-mount', this, {
      optional: false,
      name: POP,
      valid: this.checkPopValid(),
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

    checkPopValid: function() {
      return this.startDate < this.endDate
    },

    validatePop: function() {
      this.popValid = this.checkPopValid()
      this.showPopError = !this.popValid
      emitEvent('field-change', this, {
        name: POP,
        valid: this.checkPopValid(),
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
        } else if (event.name.includes(START_DATE)) {
          this.startDate = new Date(event.value)
          this.validatePop()
        } else if (event.name.includes(END_DATE)) {
          this.endDate = new Date(event.value)
          this.validatePop()
        }
      }
    },
  },
}
