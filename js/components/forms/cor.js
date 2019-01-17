import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import checkboxinput from '../checkbox_input'

export default {
  name: 'cor',

  mixins: [FormMixin],

  components: {
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
      am_cor = false
    } = this.initialData

    return {
        am_cor
    }
  }
}
