import FormMixin from '../../mixins/form'
import optionsinput from '../options_input'
import textinput from '../text_input'
import checkboxinput from '../checkbox_input'

export default {
  name: 'poc',

  mixins: [FormMixin],

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
  }
}
