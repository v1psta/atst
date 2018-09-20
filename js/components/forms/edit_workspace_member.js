import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import Selector from '../selector'
import Modal from '../../mixins/modal'
import toggler from '../toggler'

export default {
  name: 'edit-workspace-member',

  mixins: [FormMixin, Modal],

  components: {
    toggler,
    Modal,
    Selector,
    textinput
  },

  props: {
    choices: Array,
    initialData: String,
  },

  data: function () {
    return {
      value: this.initialData,
      label_class: this.initialData,
    }
  },

  methods: {
    change: function (e) {
      this.value = e.target.value
    },
    displayName: function (role) {
      this.label_class = role === "no_access" ?
        "label" : "label label--success"

      return role.replace(/[_]/g, " ")
    },
    cancel: function (current_role, selected_role) {
      if (current_role != selected_role) {
        this.value = current_role
      }
    }
  },
}
