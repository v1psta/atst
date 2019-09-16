import ally from 'ally.js'

import DateSelector from '../date_selector'
import FormMixin from '../../mixins/form'
import Modal from '../../mixins/modal'
import StickyMixin from '../../mixins/sticky'
import MultiStepModalForm from './multi_step_modal_form'
import checkboxinput from '../checkbox_input'
import levelofwarrant from '../levelofwarrant'
import multicheckboxinput from '../multi_checkbox_input'
import optionsinput from '../options_input'
import SemiCollapsibleText from '../semi_collapsible_text'
import textinput from '../text_input'
import ToForm from './to_form.js'
import toggler from '../toggler'
import uploadinput from '../upload_input'

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
    SemiCollapsibleText,
    textinput,
    ToForm,
    toggler,
    uploadinput,
  },
  mixins: [FormMixin, StickyMixin],
}
