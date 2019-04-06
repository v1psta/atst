import ally from 'ally.js'

export default {
  methods: {
    closeModal: function(name) {
      this.activeModal = null
      this.$emit('modalOpen', false)
      if (this.allyHandler) this.allyHandler.disengage()
    },

    openModal: function(name) {
      this.activeModal = name
      this.$root.$emit('modalOpen', { isOpen: true, name: name })
      const idSelector = `#${this.modalId}`

      this.allyHandler = ally.maintain.disabled({
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
      return !!this.activeModal ? `modal--${this.activeModal}` : null
    },
  },
}
