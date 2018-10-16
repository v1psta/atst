import { VPopover } from 'v-tooltip'

export default {
  name: 'selector',

  components: {
    VPopover
  },

  props: {
    choices: Array,
    defaultLabel: String,
    initialErrors: Array,
    initialChoice: {
      type: String,
      default: null
    }
  },

  data: function () {
    return {
      value: this.initialChoice || null,
      showError: (this.initialErrors && this.initialErrors.length) || false
    }
  },

  computed: {
    label: function () {
      if (this.value) {
        const selectedChoice = this.choices.find((choice) => {
          return this.value === choice[0]
        })[1]
        return selectedChoice.name
      } else {
        return this.defaultLabel
      }
    }
  },

  methods: {
    change: function (value) {
      console.log('change', value)
      this.value = value
      this.showError = false
      setTimeout(() => this.$refs.popover.hide(), 300)
    },

    handleClickOption: function (e) {
      console.log('click', e)
      this.change(e.target.value)
    },

    handleSwitchOption: function (e) {
      console.log('switch', e)
      this.value = e.target.value
    },

    handleEnterOption: function (e) {
      console.log('enter', e)
      e.stopPropagation()
      this.change(e.target.value)
      return false
    },

    handleButtonArrowDown: function (e) {
      this.$refs.popover.show()
    }
  },
}
