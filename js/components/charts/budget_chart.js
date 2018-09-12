import { format } from 'date-fns'
import { abbreviateDollars, formatDollars } from '../../lib/dollars'

const TOP_OFFSET = 20
const BOTTOM_OFFSET = 60
const CHART_HEIGHT = 360

export default {
  name: 'budget-chart',
  props: {
    currentMonth: String,
    months: Object,
    budget: String
  },

  data: function () {
    const heightScale = this.budget / (CHART_HEIGHT - TOP_OFFSET - BOTTOM_OFFSET)
    return {
      numMonths: 10,
      focusedMonthPosition: 4,
      height: CHART_HEIGHT,
      heightScale,
      budgetHeight: CHART_HEIGHT - BOTTOM_OFFSET - (this.budget / heightScale),
      baseHeight: CHART_HEIGHT - BOTTOM_OFFSET,
      width: 0,
      displayedMonths: [],
      spendPath: '',
      projectedPath: '',
      displayBudget: formatDollars(parseFloat(this.budget))
    }
  },

  mounted: function () {
    this._setDisplayedMonths()
    this._setMetrics()
    addEventListener('resize', this._setMetrics)
  },

  methods: {
    _setMetrics: function () {
      this.width = this.$refs.panel.clientWidth
      this.spendPath = ''
      this.projectedPath = ''

      let lastSpend = 0
      let lastSpendPoint = ''

      for (let i = 0; i < this.numMonths; i++) {
        const { metrics, budget } = this.displayedMonths[i]
        const blockWidth = (this.width / this.numMonths)
        const blockX = blockWidth * i
        const spend = budget
          ? budget.spend || lastSpend
          : 0
        const cumulative = budget
          ? budget.cumulative || budget.projected
          : 0
        const barHeight = spend / this.heightScale
        lastSpend = spend
        const cumulativeY = this.height - (cumulative / this.heightScale) - BOTTOM_OFFSET
        const cumulativeX = blockX + blockWidth/2
        const cumulativePoint = `${cumulativeX} ${cumulativeY}`

        this.displayedMonths[i].metrics = Object.assign(metrics, {
          blockWidth,
          blockX,
          barHeight,
          barWidth: 30,
          barX: blockX + (blockWidth/2 - 15),
          barY: this.height - barHeight - BOTTOM_OFFSET,
          cumulativeR: 2.5,
          cumulativeY,
          cumulativeX
        })

        if (budget && budget.spend) {
          this.spendPath += this.spendPath === '' ? 'M' : ' L'
          this.spendPath += cumulativePoint
          lastSpendPoint = cumulativePoint
        }

        if (budget && budget.projected) {
          this.projectedPath += this.projectedPath === '' ? `M${lastSpendPoint} L` : ' L'
          this.projectedPath += cumulativePoint
        }
      }
    },

    _setDisplayedMonths: function () {
      const [month, year] = this.currentMonth.split('/')
      const monthsRange = []
      const monthsBack = this.focusedMonthPosition
      const monthsForward = this.numMonths - this.focusedMonthPosition - 1
      const start = new Date(year, month - 1 - monthsBack)

      let previousAmount = 0

      for (let i = 0; i < this.numMonths; i++) {
        const date = new Date(start.getFullYear(), start.getMonth() + i)
        const index = format(date, 'MM/YYYY')
        const budget = this.months[index] || null
        const spendAmount = budget ? budget.spend || previousAmount : 0
        const cumulativeAmount = budget ? budget.cumulative || budget.projected : 0
        previousAmount = spendAmount

        monthsRange.push({
          budget,
          spendAmount: formatDollars(spendAmount),
          abbreviatedSpend: abbreviateDollars(spendAmount),
          cumulativeAmount: formatDollars(cumulativeAmount),
          abbreviatedCumulative: abbreviateDollars(cumulativeAmount),
          date: {
            monthIndex: format(date, 'M'),
            month: format(date, 'MMM'),
            year: format(date,'YYYY')
          },
          isHighlighted: this.currentMonth === index,
          metrics: {
            blockWidth: 0,
            blockX: 0,
            barHeight: 0,
            barWidth: 0,
            barX: 0,
            barY: 0,
            cumulativeY: 0,
            cumulativeX: 0,
            cumulativeR: 0
          }
        })

      }
      this.displayedMonths = monthsRange
    }
  }
}
