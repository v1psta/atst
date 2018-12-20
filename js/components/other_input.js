import FormMixin from '../mixins/form'
import textinput from '../components/text_input'

export default {
  name: 'otherinput',

  mixins: [FormMixin],

  components: {
    textinput,
  },

  props: {
    initialData: {
      type: Array,
      default: () => ({})
    }
  },

  data: function () {
    const {
      other = true
    } = this.initialData

    return {
        other
    }
  }
}
