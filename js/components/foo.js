import bar from './bar'

export default {
  name: "foo",

  components: {
    bar,
  },

  data: function() {
    return {
      foocontent: "hello"
    }
  }
}
