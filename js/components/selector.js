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
      return this.value
        ? this.choices.find((choice) => {
          return this.value === choice[0]
        })[1]
        : this.defaultLabel
    }
  },

  methods: {
    change: function (e) {
      this.value = e.target.value
      this.showError = false
      setTimeout(() => this.$refs.popover.hide(), 300)
    }
  },
}
