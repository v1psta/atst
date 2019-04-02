import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'
import DateSelector from '../date_selector'
import MultiStepModalForm from './multi_step_modal_form'
import multicheckboxinput from '../multi_checkbox_input'
import funding from './funding'
import checkboxinput from '../checkbox_input'
import levelofwarrant from '../levelofwarrant'

export default {
  name: 'base-form',
  components: {
    textinput,
    optionsinput,
    DateSelector,
    MultiStepModalForm,
    multicheckboxinput,
    funding,
    checkboxinput,
    levelofwarrant,
  },
  mixins: [FormMixin],
}
