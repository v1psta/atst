import ally from 'ally.js'

import DateSelector from '../date_selector'
import FormMixin from '../../mixins/form'
import Modal from '../../mixins/modal'
import MultiStepModalForm from './multi_step_modal_form'
import checkboxinput from '../checkbox_input'
import levelofwarrant from '../levelofwarrant'
import multicheckboxinput from '../multi_checkbox_input'
import optionsinput from '../options_input'
import textinput from '../text_input'
import uploadinput from '../upload_input'
import toggler from '../toggler'

export default {
  name: 'base-form',
  components: {
    DateSelector,
    Modal,
    MultiStepModalForm,
    checkboxinput,
    levelofwarrant,
    multicheckboxinput,
    optionsinput,
    textinput,
    toggler,
    uploadinput,
  },
  mixins: [FormMixin],
}
