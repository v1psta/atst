import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import { conformToMask } from 'vue-text-mask'

import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'

export default {
  name: 'details-of-use',

  mixins: [FormMixin],

  components: {
    textinput,
    optionsinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },

  data: function() {
    const {
      estimated_monthly_spend = 0,
      jedi_migration = '',
      technical_support_team = '',
    } = this.initialData

    return {
      estimated_monthly_spend,
      jedi_migration,
      technical_support_team,
    }
  },

  computed: {
    annualSpend: function() {
      const monthlySpend = this.estimated_monthly_spend || 0
      return monthlySpend * 12
    },
    annualSpendStr: function() {
      return this.formatDollars(this.annualSpend)
    },
    jediMigrationOptionSelected: function() {
      return this.jedi_migration !== ''
    },
    isJediMigration: function() {
      return this.jedi_migration === 'yes'
    },
    hasTechnicalSupportTeam: function() {
      return this.technical_support_team === 'yes'
    },
  },

  methods: {
    formatDollars: function(intValue) {
      const mask = createNumberMask({ prefix: '$', allowDecimal: true })
      return conformToMask(intValue.toString(), mask).conformedValue
    },
  },
}
