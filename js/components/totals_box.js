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
      return formatDollars(this.obligated)
    },
    formattedContractAmount: function() {
      return formatDollars(this.contractAmount)
    },
  },
}
