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
    initialErrors: {
      type: Boolean,
    },
  },

  data: function() {
    return {
      attachment: this.initialData || null,
      showErrors: this.initialErrors,
    }
  },

  methods: {
    showUploadInput: function() {
      this.showUpload = true
    },
    addAttachment: function(e) {
      this.attachment = e.target.value
      this.showErrors = false
    },
    removeAttachment: function(e) {
      e.preventDefault()
      this.attachment = null
      this.$refs.attachmentInput.value = null
      this.showErrors = false
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
