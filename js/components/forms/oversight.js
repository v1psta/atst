import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import checkboxinput from '../checkbox_input'

const cordata = {
  name: 'cordata',

  components: {
    textinput,
    checkboxinput,
  },

  mixins: [FormMixin],

  props: {
    initialCorInvite: Boolean,
  },

  data: function() {
    return {
      cor_invite: this.initialCorInvite,
    }
  },
}

export default {
  name: 'oversight',

  mixins: [FormMixin],

  components: {
    textinput,
    checkboxinput,
    cordata,
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
