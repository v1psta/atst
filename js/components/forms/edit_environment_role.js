import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import Selector from '../selector'
import Modal from '../../mixins/modal'
import toggler from '../toggler'


export default {
  name: 'edit-environment-role',

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
    revoke: Boolean,
  },

  data: function () {
    return {
      new_role: this.initialData,
    }
  },

  methods: {
    change: function (e) {
      this.new_role = e.target.value
    },
    cancel: function () {
      this.new_role = this.initialData
    },
  },

  watch: {
    revoke: function (val) {
      if (val) {
        this.new_role = ""
      }
    }
  },

  computed: {
    displayName: function () {
      const newRole = this.newRole
      for (var arr in this.choices) {
        if (this.choices[arr][0] == newRole) {
          return this.choices[arr][1].name
        }
      }
    },
    label_class: function () {
      return this.newRole === "" ?
        "label" : "label label--success"
    },
    newRole: function () {
      return this.new_role
    }
  },
}
