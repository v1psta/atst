import { VPopover } from 'v-tooltip'

const SelectorInput = {
  name: 'SelectorInput',
  props: {
    name: String,
    value: String,
    label: String,
    description: String,
    selected: Boolean,
    handleChange: Function,
    handleEnter: Function,
    handleEsc: Function
  },

  computed: {
    id: function () {
      return `${this.name}_${this.value}`
    }
  },

  methods: {
    onChange: function (e) {
      this.handleChange(this.value)
    },

    onEnter: function (e) {
      this.handleEnter()
    },

    onEsc: function (e) {
      this.handleEsc()
    }
  }
}


export default {
  name: 'selector',

  components: {
    VPopover,
    SelectorInput
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
      currentChoice: this.initialChoice || null,
      showError: (this.initialErrors && this.initialErrors.length) || false,
      usingKeyboard: false
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
      this.value = value
      this.showError = false
    },

    onShow: function () {
      setTimeout(() => { // timeout is a hack to make focus work in Chrome
        if (this.$refs.choices.find(choice => choice.selected)) {
          this.$refs.choices.find(choice => choice.selected).$refs.input[0].focus()
        } else {
          this.$refs.choices[0].$refs.input[0].focus()
        }
      }, 100)
    },

    enter: function () {
      this.$refs.popover.hide()
    },

    esc: function () {
      this.value = this.currentChoice
      this.usingKeyboard = false
      this.$refs.popover.hide()
    },

    handleEnterOption: function (e) {
      this.change(e.target.value)
      this.currentChoice = e.target.value
      this.usingKeyboard = false
      this.$refs.popover.hide()
    },

    handleButtonArrowDown: function (e) {
      this.usingKeyboard = true
      this.$refs.popover.show()
    }
  },
}
