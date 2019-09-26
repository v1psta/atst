import Vue from 'vue'
import { getDaysInMonth } from 'date-fns'
import { emitEvent } from '../lib/emitters'

let paddedNumber = function(number) {
  if ((number + '').length === 1) {
    return `0${number}`
  } else {
    return number
  }
}

export default {
  name: 'date-selector',

  props: {
    initialday: { type: String },
    initialmonth: { type: String },
    initialyear: { type: String },
    mindate: { type: String },
    maxdate: { type: String },
    nameTag: { type: String },
    watch: {
      type: Boolean,
      default: false,
    },
    optional: {
      type: Boolean,
      default: true,
    },
  },

  data: function() {
    return {
      day: this.initialday,
      month: this.initialmonth,
      year: this.initialyear,
      name: this.nameTag,
    }
  },

  created: function() {
    emitEvent('field-mount', this, {
      optional: this.optional,
      name: this.name,
      valid: this.isDateValid,
    })
  },

  watch: {
    month(newMonth, oldMonth) {
      if (!!newMonth && newMonth.length > 2) {
        this.month = oldMonth
      } else {
        this.month = newMonth
      }
    },

    day(newDay, oldDay) {
      if (!!newDay && newDay.length > 2) {
        this.day = oldDay
      } else {
        this.day = newDay
      }
    },

    year(newYear, oldYear) {
      if (!!newYear && newYear.length > 4) {
        this.year = oldYear
      } else {
        this.year = newYear
      }
    },
  },

  computed: {
    formattedDate: function() {
      let day = paddedNumber(this.day)
      let month = paddedNumber(this.month)

      if (!day || !month || !this.year) {
        return null
      }

      return `${month}/${day}/${this.year}`
    },

    isMonthValid: function() {
      let _month = parseInt(this.month)
      let valid = _month >= 0 && _month <= 12
      return valid
    },

    isDayValid: function() {
      let _day = parseInt(this.day)
      let valid = _day >= 0 && _day <= this.daysMaxCalculation
      return valid
    },

    isYearValid: function() {
      // Emit a change event
      let valid
      let minYear = this.mindate ? this.minDateParsed.getFullYear() : null
      let maxYear = this.maxdate ? this.maxDateParsed.getFullYear() : null

      if (minYear && maxYear) {
        valid = this.year >= minYear && this.year <= maxYear
      } else {
        valid = parseInt(this.year) >= 1
      }

      return valid
    },

    isWithinDateRange: function() {
      let _mindate = this.mindate ? Date.parse(this.mindate) : null
      let _maxdate = this.maxdate ? Date.parse(this.maxdate) : null
      let _dateTimestamp = Date.UTC(this.year, this.month - 1, this.day)

      if (_mindate !== null && _mindate >= _dateTimestamp) {
        return false
      }

      if (_maxdate !== null && _maxdate <= _dateTimestamp) {
        return false
      }

      return true
    },

    isDateValid: function() {
      return (
        !!this.day &&
        !!this.month &&
        !!this.year &&
        this.isDayValid &&
        this.isMonthValid &&
        this.isYearValid &&
        this.isWithinDateRange
      )
    },

    isDateComplete: function() {
      return !!this.day && !!this.month && !!this.year && this.year > 999
    },

    daysMaxCalculation: function() {
      switch (parseInt(this.month)) {
        case 2: // February
          if (this.year) {
            return getDaysInMonth(new Date(this.year, this.month - 1))
          } else {
            return 29
          }
          break

        case 4: // April
        case 6: // June
        case 9: // September
        case 11: // November
          return 30
          break

        default:
          // All other months, or null, go with 31
          return 31
      }
    },

    minError: function() {
      if (this.isDateComplete) {
        return this.minDateParsed > this.dateParsed
      }

      return false
    },

    maxError: function() {
      if (this.isDateComplete) {
        return this.maxDateParsed < this.dateParsed
      }

      return false
    },

    maxDateParsed: function() {
      return new Date(this.maxdate)
    },

    minDateParsed: function() {
      return new Date(this.mindate)
    },

    dateParsed: function() {
      return new Date(this.formattedDate)
    },
  },

  methods: {
    onInput: function(e) {
      emitEvent('field-change', this, {
        value: this.formattedDate,
        name: this.name,
        watch: this.watch,
        valid: this.isDateValid,
      })

      this.$emit('date-change', {
        value: this.formattedDate,
        name: this.name,
        valid: this.isDateValid,
      })
    },
  },

  render: function(createElement) {
    return createElement('p', 'Please implement inline-template')
  },
}
