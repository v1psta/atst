export default {
  name: 'delete-confirmation',

  data: function() {
    return {
      deleteText: '',
    }
  },

  computed: {
    valid: function() {
      return this.deleteText.toLowerCase() === 'delete'
    },
  },
}
