import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import { conformToMask } from 'vue-text-mask'

import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'

export default {
  name: 'funding',

  mixins: [FormMixin],

  components: {
    textinput,
    optionsinput
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({})
    }
  },

  data: function () {
    const {
      clin_01 = 0,
      clin_02 = 0,
      clin_03 = 0,
      clin_04 = 0,
    } = this.initialData

    return {
      clin_01,
      clin_02,
      clin_03,
      clin_04,
    }
  },

  computed: {
    totalBudget: function () {
      return [this.clin_01, this.clin_02, this.clin_03, this.clin_04].reduce(
        function(acc, curr) {
          curr = !curr ? 0 : parseInt(curr)
          return acc + curr;
        }, 0
      )
    },
    totalBudgetStr: function () {
      return this.formatDollars(this.totalBudget);
    },
  },

  methods: {
    formatDollars: function (intValue) {
      const mask = createNumberMask({ prefix: '$', allowDecimal: true })
      return conformToMask(intValue.toString(), mask).conformedValue
    },
    updateBudget: function() {
      document.querySelector('#to-target').innerText = this.totalBudgetStr
    }
  },

  watch: {
    clin_01: 'updateBudget',
    clin_02: 'updateBudget',
    clin_03: 'updateBudget',
    clin_04: 'updateBudget',
  },

  mounted: function() {
    this.updateBudget()
  }
}
