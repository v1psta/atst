import FormMixin from '../../mixins/form'
import Modal from '../../mixins/modal'
import toggler from '../toggler'
import EditEnvironmentRole from './edit_environment_role'

export default {
  name: 'edit-project-roles',

  mixins: [FormMixin, Modal],

  components: {
    toggler,
    EditEnvironmentRole,
  },

  props: {
      name: String
  },

  data: function() {
    return { revoke: false }
  },

  methods: {
    doRevoke: function () {
      // This is being used to send an event to the edit-environment-role child component.
      // We'll toggle this back on the next line so that it can be used again.
      this.revoke = true
      setTimeout(() => { this.revoke = false }, 25)
    }
  }
}
