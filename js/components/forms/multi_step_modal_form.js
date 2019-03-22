import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'
import Selector from '../selector'
import Modal from '../../mixins/modal'
import toggler from '../toggler'

export default {
  name: 'multi-step-modal-form',

  mixins: [FormMixin, Modal],

  components: {
    toggler,
    Modal,
    Selector,
    textinput,
    optionsinput,
  },

  props: {},

  data: function() {
    return {
      step: 0,
    }
  },

  mounted: function() {
    return {}
  },

  methods: {
    next: function() {
      this.step += 1
    },
    goToStep: function(step) {
      this.step = step
    },
  },

  computed: {},
}
