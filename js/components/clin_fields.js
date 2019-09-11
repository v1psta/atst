import * as R from 'ramda'
import { format } from 'date-fns'

import DateSelector from './date_selector'
import { emitEvent } from '../lib/emitters'
import Modal from '../mixins/modal'
import optionsinput from './options_input'
import textinput from './text_input'
import clindollaramount from './clin_dollar_amount'

const TOTAL_AMOUNT = 'total_amount'
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
    clindollaramount,
  },

  mixins: [Modal],

  props: {
    initialClinIndex: Number,
    initialTotal: {
      type: Number,
      default: 0,
    },
    initialObligated: {
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
    contractStart: {
      type: String,
      required: true,
    },
    contractEnd: {
      type: String,
      required: true,
    },
  },

  data: function() {
    const start = !!this.initialStartDate
      ? new Date(this.initialStartDate)
      : undefined
    const end = !!this.initialEndDate
      ? new Date(this.initialEndDate)
      : undefined
    const fundingValidation =
      this.initialObligated && this.initialTotal
        ? false
        : this.initialObligated <= this.initialTotal
    const popValidation = !this.initialStartDate ? false : start < end
    const clinNumber = !!this.initialClinNumber
      ? this.initialClinNumber
      : undefined
    const contractStartDate = new Date(this.contractStart)
    const contractEndDate = new Date(this.contractEnd)

    return {
      clinIndex: this.initialClinIndex,
      clinNumber: clinNumber,
      startDate: start,
      endDate: end,
      popValid: popValidation,
      startDateValid: false,
      endDateValid: false,
      contractStartDate: contractStartDate,
      contractEndDate: contractEndDate,
      clinNumber: clinNumber,
      showClin: true,
      popErrors: [],
      validations: [
        {
          func: this.popDateOrder,
          message: 'PoP start date must be before end date.',
        },
        {
          func: this.popStartsAfterContract,
          message: `PoP start date must be on or after ${format(
            contractStartDate,
            'MMM D, YYYY'
          )}.`,
        },
        {
          func: this.popEndsBeforeContract,
          message: `PoP end date must be before or on ${format(
            contractEndDate,
            'MMM D, YYYY'
          )}.`,
        },
      ],
      totalAmount: this.initialTotal || 0,
      obligatedAmount: this.initialObligated || 0,
      fundingValid: fundingValidation,
    }
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  created: function() {
    emitEvent('clin-change', this, {
      id: this._uid,
      obligatedAmount: this.initialObligated,
      totalAmount: this.initialTotal,
    })
    emitEvent('field-mount', this, {
      optional: false,
      name: 'clins-' + this.clinIndex + '-' + POP,
      valid: this.checkPopValid(),
    })
    emitEvent('field-mount', this, {
      optional: false,
      name: TOTAL_AMOUNT,
      valid: this.checkFundingValid(),
    })
    emitEvent('field-mount', this, {
      optional: false,
      name: OBLIGATED_AMOUNT,
      valid: this.checkFundingValid(),
    })
  },

  methods: {
    clinChangeEvent: function() {
      emitEvent('clin-change', this, {
        id: this._uid,
        obligatedAmount: this.initialObligated,
        totalAmount: this.initialTotal,
      })
    },

    checkPopValid: function() {
      return (
        this.popDateOrder() &&
        this.popStartsAfterContract() &&
        this.popEndsBeforeContract()
      )
    },

    validatePop: function() {
      this.popValid = this.checkPopValid()
      emitEvent('field-change', this, {
        name: 'clins-' + this.clinIndex + '-' + POP,
        valid: this.popValid,
      })

      this.popErrors = R.pipe(
        R.map(validation =>
          !validation.func() ? validation.message : undefined
        ),
        R.filter(Boolean)
      )(this.validations)
    },

    popStartsAfterContract: function() {
      if (this.startDateValid) {
        return this.startDate >= this.contractStartDate
      }
      return true
    },

    popEndsBeforeContract: function() {
      if (this.endDateValid) {
        return this.endDate <= this.contractEndDate
      }
      return true
    },

    popDateOrder: function() {
      if (!!this.startDate && !!this.endDate) {
        return this.startDate < this.endDate
      }
      return true
    },

    checkFundingValid: function() {
      return this.obligatedAmount <= this.totalAmount
    },

    validateFunding: function() {
      if (this.totalAmount && this.obligatedAmount) {
        this.fundingValid = this.checkFundingValid()
      }

      emitEvent('field-change', this, {
        name: OBLIGATED_AMOUNT,
        valid: this.checkFundingValid(),
      })
    },

    handleFieldChange: function(event) {
      if (this._uid === event.parent_uid) {
        if (event.name.includes(TOTAL_AMOUNT)) {
          this.totalAmount = parseFloat(event.value)
          this.validateFunding()
        } else if (event.name.includes(OBLIGATED_AMOUNT)) {
          this.obligatedAmount = parseFloat(event.value)
          this.validateFunding()
        } else if (event.name.includes(START_DATE)) {
          if (!!event.value) this.startDate = new Date(event.value)
          if (!!event.valid) this.startDateValid = event.valid
          this.validatePop()
        } else if (event.name.includes(END_DATE)) {
          if (!!event.value) this.endDate = new Date(event.value)
          if (!!event.valid) this.endDateValid = event.valid
          this.validatePop()
        } else if (event.name.includes(NUMBER)) {
          this.clinNumber = event.value
        }
      }
    },

    removeClin: function() {
      this.showClin = false
      emitEvent('remove-clin', this, {
        clinIndex: this.clinIndex,
      })
      this.closeModal('remove_clin')
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
    percentObligated: function() {
      const percentage = (this.obligatedAmount / this.totalAmount) * 100
      if (!!percentage) {
        if (percentage > 0 && percentage < 1) {
          return '<1%'
        } else if (percentage > 99 && percentage < 100) {
          return '>99%'
        } else {
          return `${percentage.toFixed(0)}%`
        }
      } else {
        return '0%'
      }
    },

    removeModalId: function() {
      return `remove-clin-${this.clinIndex}`
    },
  },
}
