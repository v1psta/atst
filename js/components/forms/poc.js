import optionsinput from '../options_input'
import textinput from '../text_input'

export default {
  name: 'poc',

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
      am_poc = 'no'
    } = this.initialData

    return {
        am_poc
    }
  },

  mounted: function () {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  computed: {
    amPOC: function () {
        return this.am_poc === 'yes'
    },
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
