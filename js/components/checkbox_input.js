import { emitEvent } from '../lib/emitters'

export default {
  name: 'checkboxinput',

  props: {
    name: String,
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
