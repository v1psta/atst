export default {
  name: 'toggler',

  data: function () {
    return {
      isVisible: false
    }
  },

  render: function (createElement) {
    return createElement( this.$vnode.data.tag, [
      this.$scopedSlots.default({
        isVisible: this.isVisible,
        toggle: this.toggle
      })
    ])
  },

  methods: {
    toggle: function (e) {
      this.isVisible = !this.isVisible
    }
  },

  mounted: function () {
    console.log(this)
  }
}
