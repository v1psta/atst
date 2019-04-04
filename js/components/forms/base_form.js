import ally from 'ally.js'

import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'
import DateSelector from '../date_selector'
import MultiStepModalForm from './multi_step_modal_form'
import multicheckboxinput from '../multi_checkbox_input'
import checkboxinput from '../checkbox_input'
import levelofwarrant from '../levelofwarrant'

export default {
  name: 'base-form',
  components: {
    textinput,
    optionsinput,
    DateSelector,
    MultiStepModalForm,
    multicheckboxinput,
    checkboxinput,
    levelofwarrant,
  },
  mixins: [FormMixin],
  methods: {
    closeModal: function(name) {
      this.activeModal = null
      this.$root.$emit('modalOpen', false)
      if (this.$root.allyHandler) this.$root.allyHandler.disengage()
    },

    openModal: function(name) {
      this.$root.activeModal = name
      this.$root.$emit('modalOpen', true)
      const idSelector = `#${this.$root.modalId}`

      this.$root.allyHandler = ally.maintain.disabled({
        filter: idSelector,
      })
    },
  },
  data: function() {
    return {
      activeModal: null,
      allyHandler: null,
    }
  },
  computed: {
    modalId: function() {
      return !!this.$root.activeModal
        ? `modal--${this.$root.activeModal}`
        : null
    },
  },
}
