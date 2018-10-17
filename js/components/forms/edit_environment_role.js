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
      e.preventDefault()
      this.new_role = this.revoke ? "" : e.target.value
    },
    cancel: function () {
      this.new_role = this.initialData
    },
    actualRole: function () {
      return this.revoke ? null : this.new_role
    }
  },

  computed: {
    displayName: function () {
      const roleName = this.actualRole()
      for (var arr in this.choices) {
        if (this.choices[arr][0] == roleName) {
          return this.choices[arr][1].name
        }
      }
      return roleName ? roleName : "no access"
    },
    label_class: function () {
      return this.displayName === "no access" ?
        "label" : "label label--success"
    },
    newRole: function () {
      return this.actualRole()
    }
  },
}
