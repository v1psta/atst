import ally from 'ally.js'

export default {
  methods: {
    closeModal: function(name) {
      this.activeModal = null
      this.$root.$emit('modalOpen', { isOpen: false, name: name })
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

    // TODO: activeModal should be tracked on the root
    handleModalOpen: function(event) {
      if (!event.isOpen) {
        this.activeModal = null
      }
    },
  },

  mounted: function() {
    this.$root.$on('modalOpen', this.handleModalOpen)
  },

  data: function() {
    // TODO: only the root component should know about the activeModal
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
