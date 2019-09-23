import DateSelector from './date_selector'

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
      startDate: this.initialStartDate,
      endDate: this.initialEndDate,
      startValid: false,
      endValid: false,
      minStartDate: this.initialMinStartDate,
      maxStartDate: this.initialMaxEndDate,
      minEndDate: this.initialMinStartDate,
      maxEndDate: this.initialMaxEndDate,
    }
  },
}
