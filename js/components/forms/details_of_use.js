import textinput from '../text_input'
import optionsinput from '../options_input'

export default {
  name: 'details-of-use',

  components: {
    textinput,
    optionsinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({})
    }
  },

  data: function () {
    const {
      estimated_monthly_spend = 0,
      jedi_migration = '',
      technical_support_team = ''
    } = this.initialData

    return {
      estimated_monthly_spend,
      jedi_migration,
      technical_support_team
    }
  },

  mounted: function () {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  computed: {
    annualSpend: function () {
      const monthlySpend = this.estimated_monthly_spend || 0
      return monthlySpend * 12
    },
    jediMigrationOptionSelected: function () {
      return this.jedi_migration !== ''
    },
    isJediMigration: function () {
      return this.jedi_migration === 'yes'
    },
    hasTechnicalSupportTeam: function () {
      return this.technical_support_team === 'yes'
    }
  },

  methods: {
    handleFieldChange: function (event) {
      const { value, name } = event
      if (typeof this[name] !== undefined) {
        this[name] = value
      }
    },
  }
}
