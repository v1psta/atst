import EnvironmentRole from '../environment_role'
import optionsinput from '../options_input'

export default {
  name: 'team-member',

  props: {
    initialValue: String,
  },

  components: {
    EnvironmentRole,
    optionsinput,
  },

  data: function() {
    return {
      edit_access: this.initialValue.includes('edit') ? true : false,
      open: false,
    }
  },

  methods: {
    flip: function() {
      this.edit_access = !this.edit_access
    },
    toggle: function() {
      this.open = !this.open
    },
  },
}
