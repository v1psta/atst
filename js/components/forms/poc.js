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
    return {
        am_poc: "no"
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
      console.log(value, name)
      if (typeof this[name] !== undefined) {
        this[name] = value
      }
    },
  }
}
