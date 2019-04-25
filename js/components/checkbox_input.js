import { emitEvent } from '../lib/emitters'

export default {
  name: 'checkboxinput',

  components: {
    checkboxinput: this,
  },

  props: {
    name: String,
    initialChecked: Boolean,
  },

  data: function() {
    return {
      checked: this.initialChecked,
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
