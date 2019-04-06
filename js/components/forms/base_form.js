import ally from 'ally.js'

import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'
import DateSelector from '../date_selector'
import MultiStepModalForm from './multi_step_modal_form'
import multicheckboxinput from '../multi_checkbox_input'
import checkboxinput from '../checkbox_input'
import levelofwarrant from '../levelofwarrant'
import Modal from '../../mixins/modal'

export default {
  name: 'base-form',
  components: {
    textinput,
    optionsinput,
    DateSelector,
    MultiStepModalForm,
    multicheckboxinput,
    checkboxinput,
    levelofwarrant,
    Modal,
  },
  mixins: [FormMixin, Modal],
}
