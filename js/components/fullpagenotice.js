export default {
  name: 'fullpagenotice',

  data: function() {
    return {
      visible: false,
    }
  },

  methods: {
    displayNotice: function() {
      this.visible = true
    },
  },
}
