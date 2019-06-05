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
      attachment: pdf || null,
    }
  },

  methods: {
    showUploadInput: function() {
      this.showUpload = true
    },
    addAttachment: function(e) {
      this.attachment = e.target.value
    },
    removeAttachment: function(e) {
      e.preventDefault()
      this.attachment = null
      this.$refs.attachmentInput.value = null
    },
  },

  computed: {
    baseName: function() {
      if (this.attachment) {
        return this.attachment.split(/[\\/]/).pop()
      }
    },
    hasAttachment: function() {
      return !!this.attachment
    },
  },
}
