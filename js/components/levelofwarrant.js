import textinput from './text_input'
import checkboxinput from './checkbox_input'
import FormMixin from '../mixins/form'

export default {
  mixins: [FormMixin],

  components: {
    textinput,
    checkboxinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    const { unlimited_level_of_warrant = false } = this.initialData

    return {
      unlimited_level_of_warrant,
    }
  },
}
