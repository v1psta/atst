import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import { conformToMask } from 'vue-text-mask'

import FormMixin from '../mixins/form'
import textinput from './text_input'
import optionsinput from './options_input'

export default {
  name: 'uploadinput',

  mixins: [FormMixin],

  components: {
    textinput,
    optionsinput,
  },

  props: {
    initialData: {
      type: String,
    },
    uploadErrors: {
      type: Array,
      default: () => [],
    },
  },

  data: function() {
    const pdf = this.initialData

    return {
      showUpload: !pdf || this.uploadErrors.length > 0,
      showError: (this.uploadErrors.length > 0) || false,
      showValid: (this.uploadErrors.length === 0) || false,
    }
  },

  methods: {
    showUploadInput: function() {
      this.showUpload = true
    },
  },
}
