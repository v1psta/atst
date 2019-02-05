import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import { conformToMask } from 'vue-text-mask'

import FormMixin from '../mixins/form'
import textinput from './text_input'
import optionsinput from './options_input'

export default {
  name: 'upload',

  mixins: [FormMixin],

  components: {
    textinput,
    optionsinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({}),
    },
    uploadErrors: {
      type: Array,
      default: () => [],
    },
  },

  data: function() {
    const { pdf } = this.initialData

    return {
      showUpload: !pdf || this.uploadErrors.length > 0,
    }
  },

  methods: {
    showUploadInput: function() {
      this.showUpload = true
    },
  },
}
