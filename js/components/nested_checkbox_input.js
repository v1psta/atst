import { emitEvent } from '../lib/emitters'

export default {
  name: 'nestedcheckboxinput',

  props: {
    name: String,
    isParentChecked: Boolean,
  },

  data: function() {
    return {
      isChecked: false,
    }
  },

  updated: function() {
    if (!this.isParentChecked) {
      this.isChecked = false
    }
  },

  methods: {
    onInput: function(e) {
      emitEvent('field-change', this, {
        value: e.target.checked,
        name: this.name,
      })
    },
  },
}
