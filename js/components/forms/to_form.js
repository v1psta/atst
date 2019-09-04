import stickybits from 'stickybits'

import checkboxinput from '../checkbox_input'
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
    checkboxinput,
    ClinFields,
    DateSelector,
    optionsinput,
    SemiCollapsibleText,
    textinput,
    TotalsBox,
    uploadinput,
  },

  props: {
    initialClinCount: {
      type: Number,
      default: null,
    },
    initialObligated: {
      type: Number,
      default: null,
    },
    initialTotal: {
      type: Number,
      default: null,
    },
  },

  data: function() {
    const clins = this.initialClinCount == 0 ? 1 : 0
    const clinIndex = this.initialClinCount == 0 ? 0 : this.initialClinCount - 1

    return {
      clins,
      clinIndex,
      obligated: this.initialObligated || 0,
      total: this.initialTotal || 0,
      clinChildren: {},
    }
  },

  mounted: function() {
    this.$root.$on('clin-change', this.calculateClinAmounts)
    this.$root.$on('remove-clin', this.handleRemoveClin)
  },

  methods: {
    addClin: function(event) {
      ++this.clins
      ++this.clinIndex
    },

    handleRemoveClin: function(event) {
      --this.clinIndex
      console.log('removed clin')
    },

    calculateClinAmounts: function(event) {
      this.clinChildren[event.id] = {
        amount: event.amount,
        type: event.clinType,
      }

      let newTotal = 0
      let newObligated = 0
      Object.values(this.clinChildren).forEach(function(clin) {
        newTotal += clin.amount
        if (clin.type.includes('1') || clin.type.includes('3')) {
          newObligated += clin.amount
        }
      })
      this.total = newTotal
      this.obligated = newObligated
    },
  },

  directives: {
    sticky: {
      inserted: (el, binding) => {
        var customAttributes
        if (binding.expression) {
          customAttributes = JSON.parse(binding.expression)
        }
        stickybits(el, customAttributes)
      },
    },
  },
}
