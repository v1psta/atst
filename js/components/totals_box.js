import { formatDollars } from '../lib/dollars'

export default {
  name: 'totalsbox',

  props: {
    name: String,
    additionalObligated: Number,
    additionalContractAmount: Number,
  },

  data: function() {
    return {
      obligated: formatDollars(
        this.additionalObligated
      ),
      contractAmount: formatDollars(
        this.additionalContractAmount
      ),
    }
  },
}
