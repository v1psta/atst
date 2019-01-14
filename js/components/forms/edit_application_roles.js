import FormMixin from '../../mixins/form'
import Modal from '../../mixins/modal'
import toggler from '../toggler'
import EditEnvironmentRole from './edit_environment_role'

export default {
  name: 'edit-application-roles',

  mixins: [FormMixin, Modal],

  components: {
    toggler,
    EditEnvironmentRole,
  },

  props: {
    name: String,
    id: String
  },

  methods: {
    doRevoke: function () {
      this.$root.$emit('revoke-' + this.id)
    }
  }
}
