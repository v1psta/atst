import optionsinput from '../options_input'
import textinput from '../text_input'
import checkboxinput from '../checkbox_input'

export default {
  name: 'poc',

  components: {
    optionsinput,
    textinput,
    checkboxinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({})
    }
  },

  data: function () {
    const {
      am_poc = false
    } = this.initialData

    return {
        am_poc
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
