import FormMixin from '../../mixins/form'
import optionsinput from '../options_input'
import textinput from '../text_input'

export default {
  name: 'financial',

  mixins: [FormMixin],

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
  }
}
