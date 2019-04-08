import { emitFieldChange } from '../lib/emitters'

export default {
  name: 'checkboxinput',

  props: {
    name: String,
  },

  methods: {
    onInput: function(e) {
      emitFieldChange(this, { value: e.target.checked, name: this.name })
    },
  },
}
