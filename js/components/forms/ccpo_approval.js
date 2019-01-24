import textinput from '../text_input'
import LocalDatetime from '../local_datetime'

export default {
  name: 'ccpo-approval',

  components: {
    textinput,
    LocalDatetime,
  },

  props: {
    initialState: String,
  },

  data: function() {
    return {
      approving: this.initialState === 'approving',
      denying: this.initialState === 'denying',
    }
  },

  methods: {
    setReview: function(e) {
      if (e.target.value === 'approving') {
        this.approving = true
        this.denying = false
      } else {
        this.approving = false
        this.denying = true
      }
    },
  },
}
