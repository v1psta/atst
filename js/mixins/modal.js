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
      modals: {
        styleguidemodal: false,
        newprojectconfirmation: false,
        pendingfinancialverification: false,
        pendingccpoapproval: false,
      },
      activeModal: null,
    }
  }
}
