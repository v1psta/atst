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
    initialStartDate: {
      type: String,
      default: null,
    },
    initialEndDate: {
      type: String,
      default: null,
    },
    clinIndex: Number,
  },

  data: function() {
    var start = !!this.initialStartDate ? new Date(this.initialStartDate) : null
    var end = !!this.initialEndDate ? new Date(this.initialEndDate) : null
    var contractStart = new Date(this.initialMinStartDate)
    var contractEnd = new Date(this.initialMaxEndDate)

    return {
      maxStartDate: this.calcMaxStartDate(end, contractEnd),
      minEndDate: this.calcMinEndDate(start, contractStart),
    }
  },

  methods: {
    handleDateChange: function(event) {
      if (event.name.includes(START_DATE)) {
        if (event.valid != undefined && event.valid) {
          var date = new Date(event.value)
          this.minEndDate = this.calcMinEndDate(date)
        }
      } else if (event.name.includes(END_DATE)) {
        if (event.valid != undefined && event.valid) {
          var date = new Date(event.value)
          this.maxStartDate = this.calcMaxStartDate(date)
        }
      }
    },

    calcMaxStartDate: function(date, end = this.maxStartDate) {
      if (!!date && date < end) {
        return date
      } else {
        return end
      }
    },

    calcMinEndDate: function(date, start = this.minEndDate) {
      if (!!date && date > start) {
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
