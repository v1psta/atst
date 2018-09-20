export default {
  methods: {
    closeModal: function(name) {
      this.modals[name] = false
      this.$emit('modalOpen', false)
    },
    openModal: function (name) {
      this.modals[name] = true
      this.$emit('modalOpen', true)
    }
  },
  data: function() {
    return {
      modals: {
        styleguideModal: false,
        rolesModal: false,
        newProjectConfirmation: false,
        pendingFinancialVerification: false,
        pendingCCPOApproval: false,
      }
    }
  }
}
