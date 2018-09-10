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
    initialData: String
  },

  data: function () {
    return { value: this.initialData }
  },

  methods: {
    change: function (e) {
      this.value = e.target.value
    },
    readableName: function (role) {
      return role.replace(/[_]/g, " ")
    },
  },

  mounted: function () {
    console.log(this.initialData, this.choices)
  }
}
