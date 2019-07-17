import { emitEvent } from '../lib/emitters'
import nestedcheckboxinput from './nested_checkbox_input'

export default {
  name: 'checkboxinput',

  components: {
    nestedcheckboxinput,
  },

  props: {
    name: String,
    initialChecked: Boolean,
  },

  data: function() {
    return {
      isChecked: this.initialChecked,
    }
  },

  created: function() {
    emitEvent('field-mount', this, {
      optional: this.optional,
      name: this.name,
      valid: this.isChecked,
    })
  },

  methods: {
    onInput: function(e) {
      emitEvent('field-change', this, {
        value: e.target.checked,
        name: this.name,
        valid: this.isChecked,
      })
    },
  },
}
