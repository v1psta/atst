import * as d3 from 'd3'
import { format } from 'date-fns'

export default {
  name: 'budget-chart',
  props: {
    currentMonth: String,
    months: Object
  },

  data: function () {
    return {
      numMonths: 10,
      focusedMonthPosition: 4, // 5th spot in zero-based index,
      height: 300,
      width: 0,
      displayedMonths: []
    }
  },

  computed: {

  },

  mounted: function () {
    console.log(this.displayedMonths)
    this._setDisplayedMonths()
    this._setMetrics()
  },

  methods: {
    _setMetrics: function () {
      this.width = this.$refs.panel.clientWidth
      // for (let i = 0; i < this.numMonths; i++) {
      //   this.displayedMonths[i].metrics.x = (this.width / this.numMonths)
      // }
    },

    _setDisplayedMonths: function () {
      const [month, year] = this.currentMonth.split('/')
      const monthsRange = []
      const monthsBack = this.focusedMonthPosition
      const monthsForward = this.numMonths - this.focusedMonthPosition - 1
      const start = new Date(year, month - 1 - monthsBack)

      for (let i = 0; i < this.numMonths; i++) {
        const date = new Date(start.getFullYear(), start.getMonth() + i)
        const index = format(date, 'MM/YYYY')
        monthsRange.push({
          date: {
            month: format(date, 'MMM'),
            year: format(date,'YYYY')
          },
          budget: this.months[index] || null,
          isHighlighted: this.currentMonth === index,
          metrics: {
            x: 0,
            width: 0
          }
        })
      }
      this.displayedMonths = monthsRange
    }
  }
}
