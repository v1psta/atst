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
      hasInitialData: !!this.initialData,
      attachment: this.initialData || null,
      showErrors: this.initialErrors,
      changed: false,
    }
  },

  methods: {
    addAttachment: function(e) {
      this.attachment = e.target.value
      this.showErrors = false
      this.changed = true
    },
    removeAttachment: function(e) {
      e.preventDefault()
      this.attachment = null
      if (this.$refs.attachmentInput) {
        this.$refs.attachmentInput.value = null
      }
      this.showErrors = false
      this.changed = true
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
    hideInput: function() {
      return this.hasInitialData && !this.changed
    },
  },
}
