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

  props: {
    steps: Number,
  },

  data: function() {
    return {
      step: 0,
      fields: {},
      invalid: true,
    }
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleValidChange)
    this.$on('modalOpen', this.handleModalOpen)
  },

  methods: {
    next: function() {
      if (this._checkIsValid()) {
        this.step += 1
      }
    },
    goToStep: function(step) {
      if (this._checkIsValid()) {
        this.step = step
      }
    },
    handleValidChange: function(event) {
      const { name, valid } = event
      this.fields[name] = valid
      this._checkIsValid()
    },
    _checkIsValid: function() {
      const valid = !Object.values(this.fields).some(field => field === false)
      this.invalid = !valid
      return valid
    },
    handleFieldMount: function(event) {
      const { name, optional } = event
      this.fields[name] = optional
    },
    handleModalOpen: function(_bool) {
      this.step = 0
    },
    _onLastPage: function() {
      return this.step === this.steps - 1
    },
    handleSubmit: function(e) {
      if (this.invalid || !this._onLastPage()) {
        e.preventDefault()
        this.next()
      }
    },
  },

  computed: {},
}
