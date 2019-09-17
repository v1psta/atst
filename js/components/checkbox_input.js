import { emitEvent } from '../lib/emitters'

export default {
  name: 'checkboxinput',

  props: {
    name: String,
    initialChecked: Boolean,
    optional: Boolean,
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
      valid: this.optional || this.isChecked,
    })
  },

  methods: {
    onInput: function(e) {
      emitEvent('field-change', this, {
        value: e.target.checked,
        name: this.name,
        valid: this.optional || this.isChecked,
      })
    },
  },
}
