import ally from 'ally.js'

import checkboxinput from '../checkbox_input'
import DateSelector from '../date_selector'
import FormMixin from '../../mixins/form'
import levelofwarrant from '../levelofwarrant'
import Modal from '../../mixins/modal'
import multicheckboxinput from '../multi_checkbox_input'
import MultiStepModalForm from './multi_step_modal_form'
import optionsinput from '../options_input'
import textinput from '../text_input'
import toggler from '../toggler'

export default {
  name: 'base-form',
  components: {
    checkboxinput,
    DateSelector,
    levelofwarrant,
    Modal,
    multicheckboxinput,
    MultiStepModalForm,
    optionsinput,
    textinput,
    toggler,
  },
  mixins: [FormMixin],
}
