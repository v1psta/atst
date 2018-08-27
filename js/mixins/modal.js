export default {
  methods: {
    closeModal: function(name) {
      this.modals[name] = false
    },
    openModal: function (name) {
      this.modals[name] = true
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
