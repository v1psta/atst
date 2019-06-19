import { formatDollars } from '../lib/dollars'

export default {
  name: 'totalsbox',

  props: {
    name: String,
    obligated: Number,
    contractAmount: Number,
  },

  computed: {
    formattedObligated: function() {
      return formatDollars(this._filterNaN(this.obligated))
    },
    formattedContractAmount: function() {
      return formatDollars(this._filterNaN(this.contractAmount))
    },
  },

  methods: {
    _filterNaN: function(value) {
      return Number.isNaN(value) ? 0 : value
    },
  },
}
