import DateSelector from './date_selector'
import { emitEvent } from '../lib/emitters'
import optionsinput from './options_input'
import textinput from './text_input'

const JEDI_CLIN_TYPE = 'jedi_clin_type'
const OBLIGATED_AMOUNT = 'obligated_amount'
const START_DATE = 'start_date'
const END_DATE = 'end_date'
const POP = 'period_of_performance'
const NUMBER = 'number'

export default {
  name: 'clin-fields',

  components: {
    DateSelector,
    optionsinput,
    textinput,
  },

  props: {
    initialClinIndex: Number,
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
    initialClinNumber: {
      type: String,
      default: null,
    },
  },

  data: function() {
    const start = !!this.initialStartDate
      ? new Date(this.initialStartDate)
      : undefined
    const end = !!this.initialEndDate
      ? new Date(this.initialEndDate)
      : undefined
    const popValidation = !this.initialStartDate ? false : start < end
    const showPopValidation = !this.initialStartDate ? false : !popValidation
    const clinNumber = !!this.initialClinNumber
      ? this.initialClinNumber
      : undefined

    return {
      clinIndex: this.initialClinIndex,
      clinType: this.initialClinType,
      amount: this.initialAmount || 0,
      startDate: start,
      endDate: end,
      popValid: popValidation,
      showPopError: showPopValidation,
      clinNumber: clinNumber,
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
      if (!!this.startDate && !!this.endDate) {
        // only want to update popValid and showPopError if both dates are filled in
        this.popValid = this.checkPopValid()
        this.showPopError = !this.popValid
      }

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
          if (!!event.value) this.startDate = new Date(event.value)
          this.validatePop()
        } else if (event.name.includes(END_DATE)) {
          if (!!event.value) this.endDate = new Date(event.value)
          this.validatePop()
        } else if (event.name.includes(NUMBER)) {
          if (!!event.value) this.clinNumber = event.value
        }
      }
    },
  },

  computed: {
    clinTitle: function() {
      if (!!this.clinNumber) {
        return `CLIN ${this.clinNumber}`
      } else {
        return `CLIN`
      }
    },
  },
}
