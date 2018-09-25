export default {
  methods: {
    closeModal: function(name) {
      this.activeModal = null
      this.$emit('modalOpen', false)
    },
    openModal: function (name) {
      this.activeModal = name
      this.$emit('modalOpen', true)
    }
  },
  data: function() {
    return {
      activeModal: null,
    }
  }
}
