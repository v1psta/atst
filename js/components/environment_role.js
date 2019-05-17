import optionsinput from './options_input'
import { emitEvent } from '../lib/emitters'

export default {
  name: 'environment-role',

  components: {
    optionsinput,
  },

  props: {
    initialRole: String,
  },

  data: function() {
    return {
      role: this.initialRole,
      expanded: false,
    }
  },

  methods: {
    toggle: function() {
      this.expanded = !this.expanded
    },
    radioChange: function(e) {
      this.role = e.target.value
      emitEvent('field-change', this, {
        value: e.target.value,
        valid: true,
        name: this.name,
        watch: true,
      })
    },
  },
}
