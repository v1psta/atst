import ClinFields from '../clin_fields'
import DateSelector from '../date_selector'
import FormMixin from '../../mixins/form'
import optionsinput from '../options_input'
import textinput from '../text_input'

export default {
  name: 'to-form',

  mixins: [FormMixin],

  components: {
    ClinFields,
    DateSelector,
    optionsinput,
    textinput,
  },

  props: {
    initialClinCount: Number,
  },

  data: function() {
    const clins = this.initialClinCount == 0 ? [''] : []
    const clinIndex = this.initialClinCount == 0 ? 0 : this.initialClinCount - 1

    return {
      clins,
      clinIndex,
    }
    // pass initialCLINIndex in props and add one each time a clin is added...
    // this way we can keep track of the clin id for the html name/id/etc
  },

  methods: {
    addClin: function(event) {
      this.clins.push('')
      this.clinIndex = this.clinIndex + 1
    },
  },
}
