import { format } from 'date-fns'

import DateSelector from './date_selector'

const START_DATE = 'start_date'
const END_DATE = 'end_date'

export default {
  name: 'pop-date-range',

  components: {
    DateSelector,
  },

  props: {
    initialMinStartDate: String,
    initialMaxEndDate: String,
    initialStartDate: String,
    initialEndDate: String,
    clinIndex: Number,
  },

  data: function() {
    var start = new Date(this.initialStartDate)
    var end = new Date(this.initialEndDate)
    var contractStart = new Date(this.initialMinStartDate)
    var contractEnd = new Date(this.initialMaxEndDate)

    return {
      startDate: start,
      endDate: end,
      startValid: false,
      endValid: false,
      maxStartDate: this.calcMaxStartDate(end, contractEnd),
      minEndDate: this.calcMinEndDate(start, contractStart),
      contractStart: contractStart,
      contractEnd: contractEnd,
    }
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleDateChange)
  },

  methods: {
    handleDateChange: function(event) {
      if (event.name.includes(START_DATE)) {
        if (!!event.value) this.startDate = new Date(event.value)
        if (!!event.valid) this.startValid = event.valid
        if (this.startValid)
          this.minEndDate = this.calcMinEndDate(this.startDate)
      } else if (event.name.includes(END_DATE)) {
        if (!!event.value) this.endDate = new Date(event.value)
        if (!!event.valid) this.endValid = event.valid
        if (this.endValid)
          this.maxStartDate = this.calcMaxStartDate(this.endDate)
      }
    },

    calcMaxStartDate: function(date, end = this.contractEnd) {
      if (date < end) {
        return date
      } else {
        return end
      }
    },

    calcMinEndDate: function(date, start = this.contractStart) {
      if (date > start) {
        return date
      } else {
        return start
      }
    },
  },

  computed: {
    maxStartProp: function() {
      return format(this.maxStartDate, 'YYYY-MM-DD')
    },

    minEndProp: function() {
      return format(this.minEndDate, 'YYYY-MM-DD')
    },
  },
}
