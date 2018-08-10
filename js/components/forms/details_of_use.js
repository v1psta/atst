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
    return {
      jedi_migration: this.initialData.jedi_migration
    }
  },

  mounted: function () {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  computed: {
    isJediMigration: function () {
      return this.jedi_migration === 'yes'
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
