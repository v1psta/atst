import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import checkboxinput from '../checkbox_input'

export default {
  name: 'oversight',

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

  data: function() {
    const {
      am_cor = false,
      ko_invite = false,
      cor_invite = false,
      so_invite = false,
    } = this.initialData

    return {
      am_cor,
      ko_invite,
      cor_invite,
      so_invite,
    }
  },
}
