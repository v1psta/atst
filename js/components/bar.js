export default {
  name: "bar",

  props: {
    foocontent: String
  },

  data: function() {
    return {
      barcontent: ""
    }
  },

  computed: {
    fooBarContent: function() {
      return this.foocontent + " " + this.barcontent
    }
  }
}
