import stickybits from 'stickybits'

import ClinFields from '../clin_fields'
import DateSelector from '../date_selector'
import FormMixin from '../../mixins/form'
import optionsinput from '../options_input'
import SemiCollapsibleText from '../semi_collapsible_text'
import textinput from '../text_input'
import TotalsBox from '../totals_box'
import uploadinput from '../upload_input'

export default {
  name: 'to-form',

  mixins: [FormMixin],

  components: {
    ClinFields,
    DateSelector,
    optionsinput,
    SemiCollapsibleText,
    textinput,
    TotalsBox,
    uploadinput,
  },

  props: {
    initialClinCount: Number,
    initialObligated: Number,
    initialTotal: Number,
  },

  data: function() {
    const clins = this.initialClinCount == 0 ? 1 : 0
    const clinIndex = this.initialClinCount == 0 ? 0 : this.initialClinCount - 1

    return {
      clins,
      clinIndex,
      obligated: this.initialObligated || 0,
      total: this.initialTotal || 0,
    }
  },

  mounted: function() {
    this.$root.$on('clin-change', this.calculateClinAmounts)
  },

  methods: {
    addClin: function(event) {
      ++this.clins
      ++this.clinIndex
    },

    calculateClinAmounts: function (event) {
      this.total += parseFloat(event.amount - this.total)
      if (event.clinType.includes('1') || event.clinType.includes('3')) {
        this.obligated += parseFloat(event.amount - this.obligated)
      }
    },
  },

  directives: {
    sticky: {
      inserted: el => {
        stickybits(el)
      },
    },
  },
}
