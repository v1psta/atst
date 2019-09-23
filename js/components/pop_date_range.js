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
    return {
      startDate: new Date(this.initialStartDate),
      endDate: new Date(this.initialEndDate),
      startValid: false,
      endValid: false,
      minStartDate: new Date(this.initialMinStartDate),
      maxEndDate: new Date(this.initialMaxEndDate),
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
      } else if (event.name.includes(END_DATE)) {
        if (!!event.value) this.endDate = new Date(event.value)
        if (!!event.valid) this.endValid = event.valid
      }
    },

    maxStartDate: function() {
      if (this.endDate < new Date(this.initialMaxEndDate)) {
        return this.endDate
      } else {
        return this.initialMaxEndDate
      }
    },

    minEndDate: function() {
      if (this.startDate > new Date(this.initialMinStartDate)) {
        return this.startDate
      } else {
        return this.initialMinEndDate
      }
    },
  },

  computed: {
    maxStartProp: function() {
      return format(this.maxStartDate(), 'YYYY-MM-DD')
    },

    minEndProp: function() {
      return format(this.minEndDate(), 'YYYY-MM-DD')
    }
  }
}
