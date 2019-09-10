import * as R from 'ramda'
import { format } from 'date-fns'

import DateSelector from './date_selector'
import { emitEvent } from '../lib/emitters'
import Modal from '../mixins/modal'
import optionsinput from './options_input'
import textinput from './text_input'

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

  mixins: [Modal],

  props: {
    initialClinIndex: Number,
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
    const popValidation = !this.initialStartDate ? false : start < end
    const clinNumber = !!this.initialClinNumber
      ? this.initialClinNumber
      : undefined
    const contractStartDate = new Date(this.contractStart)
    const contractEndDate = new Date(this.contractEnd)

    return {
      clinIndex: this.initialClinIndex,
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
    }
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  created: function() {
    emitEvent('field-mount', this, {
      optional: false,
      name: 'clins-' + this.clinIndex + '-' + POP,
      valid: this.checkPopValid(),
    })
  },

  methods: {
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

    handleFieldChange: function(event) {
      if (this._uid === event.parent_uid) {
        if (event.name.includes(START_DATE)) {
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

    removeModalId: function() {
      return `remove-clin-${this.clinIndex}`
    },
  },
}
