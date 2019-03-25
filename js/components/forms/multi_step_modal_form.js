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
      fields: {},
    }
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleValidChange)
  },

  methods: {
    next: function() {
      if (this.isValid()) {
        this.step += 1
      }
    },
    goToStep: function(step) {
      if (this.isValid()) {
        this.step = step
      }
    },
    handleValidChange: function(event) {
      const { name, valid } = event
      this.fields[name] = valid
    },
    isValid: function() {
      return !Object.values(this.fields).some(field => field === false)
    },
    handleFieldMount: function(event) {
      const { name, optional } = event
      this.fields[name] = optional
    }
  },

  computed: {},
}
