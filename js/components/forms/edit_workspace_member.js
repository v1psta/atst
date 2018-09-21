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
      new_role: this.initialData,
    }
  },

  methods: {
    change: function (e) {
      e.preventDefault()
      this.new_role = e.target.value
    },
    cancel: function (current_role, selected_role) {
      if (current_role != selected_role) {
        this.new_role = current_role
      }
    },
  },

  computed: {
    displayName: function () {
      for (var arr in this.choices) {
        if (this.choices[arr][0] == this.new_role) {
          return this.choices[arr][1].name
        }
      }
      return this.new_role ? this.new_role : "no access"
    },
    label_class: function () {
      return this.displayName === "no access" ?
        "label" : "label label--success"
    }
  }
}
