import { set } from 'vue/dist/vue'
import { compose, sortBy, reverse, indexBy, prop, toLower } from 'ramda'

import { formatDollars } from '../../lib/dollars'
import localDatetime from '../../components/local_datetime'

const sort = (sortInfo, members) => {
  if (sortInfo.columnName === '') {
    return members
  } else {
    const sortColumn = sortInfo.columns[sortInfo.columnName]
    const sortedMembers = sortColumn.sortFunc(sortColumn.attr, members)

    return sortInfo.isAscending ? sortedMembers : reverse(sortedMembers)
  }
}

export default {
  name: 'task-order-list',

  props: {
    data: Array,
    expired: Boolean,
    funded: Boolean,
  },

  components: {
    localDatetime,
  },

  data: function() {
    const alphabeticalSort = (attr, members) => {
      const lowercaseProp = compose(
        toLower,
        prop(attr)
      )
      return sortBy(lowercaseProp, members)
    }

    const numericSort = (attr, members) => sortBy(prop(attr), members)
    const columns = [
      {
        displayName: 'Status',
        attr: 'display_status',
      },
      {
        displayName: 'Period of Performance',
        attr: 'start_date',
        sortFunc: numericSort,
        width: '50%',
        class: 'period-of-performance',
      },
      {
        displayName: 'Initial Value',
        attr: 'budget',
        class: 'table-cell--align-right',
        sortFunc: numericSort,
      },
      {
        displayName: this.expired ? 'Expired Balance' : 'Balance',
        attr: 'budget',
        class: 'table-cell--align-right',
        sortFunc: numericSort,
      },
      {
        displayName: '',
      },
    ]

    const defaultSortColumn = 'Period of Performance'
    return {
      sortInfo: {
        columnName: defaultSortColumn,
        isAscending: false,
        columns: indexBy(prop('displayName'), columns),
      },
      days_to_exp_alert_limit: 30,
    }
  },

  computed: {
    taskOrders: function() {
      return sort(this.sortInfo, this.data)
    },
  },

  methods: {
    updateSort: function(columnName) {
      // clicking a column twice toggles ascending / descending
      if (columnName === this.sortInfo.columnName) {
        this.sortInfo.isAscending = !this.sortInfo.isAscending
      }

      this.sortInfo.columnName = columnName
    },

    getColumns: function() {
      return Object.values(this.sortInfo.columns)
    },

    formatDollars: function(value) {
      return formatDollars(value, false)
    },
  },

  template: '<div></div>',
}
