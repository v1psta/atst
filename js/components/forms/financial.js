import optionsinput from '../options_input'
import textinput from '../text_input'

export default {
  name: 'financial',

  components: {
    optionsinput,
    textinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({})
    }
  },

  data: function () {
    const {
      funding_type = ""
    } = this.initialData

    return {
      funding_type
    }
  },

  mounted: function () {
    this.$root.$on('field-change', this.handleFieldChange)
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
