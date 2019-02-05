import Vue from 'vue'

import textinput from './text_input'
import checkboxinput from './checkbox_input'
import FormMixin from '../mixins/form'

export default Vue.component('levelofwarrant', {
  mixins: [FormMixin],

  components: {
    textinput,
    checkboxinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    const { unlimited_level_of_warrant = false } = this.initialData

    return {
      unlimited_level_of_warrant,
    }
  },
})
