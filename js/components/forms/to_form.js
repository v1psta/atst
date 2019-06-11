import ClinFields from '../clin_fields'
import DateSelector from '../date_selector'
import FormMixin from '../../mixins/form'
import optionsinput from '../options_input'
import textinput from '../text_input'
import uploadinput from '../upload_input'

export default {
  name: 'to-form',

  mixins: [FormMixin],

  components: {
    ClinFields,
    DateSelector,
    optionsinput,
    textinput,
    uploadinput,
  },

  props: {
    initialClinCount: Number,
  },

  data: function() {
    const clins = this.initialClinCount == 0 ? 1 : 0
    const clinIndex = this.initialClinCount == 0 ? 0 : this.initialClinCount - 1

    return {
      clins,
      clinIndex,
    }
  },

  methods: {
    addClin: function(event) {
      ++this.clins
      ++this.clinIndex
    },
  },
}
