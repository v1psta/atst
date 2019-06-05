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
    initialClinCount: String,
  },

  data: function() {
    const clins = this.initialClinCount == 0 ? [''] : []

    return {
      clins,
      clinCount: this.initalClinCount - 1,
    }
    // pass initialCLINIndex in props and add one each time a clin is added...
    // this way we can keep track of the clin id for the html name/id/etc
  },

  methods: {
    addClin: function(event) {
      this.clins.push('')
      this.clinCount = this.clinCount + 1
    },
  },
}
