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
    }
  },

  methods: {
    change: function (e) {
      this.value = e.target.value
    },
    cancel: function (current_role, selected_role) {
      if (current_role != selected_role) {
        this.value = current_role
      }
    }
  },

  computed: {
    displayName: function () {
      for (var arr in this.choices) {
        if (this.choices[arr][0] == this.value) {
          return this.choices[arr][1].name
        }
      }
      return this.value
    },
    label_class: function () {
      return this.value === "no_access" ?
        "label" : "label label--success"
    }
  }
}
