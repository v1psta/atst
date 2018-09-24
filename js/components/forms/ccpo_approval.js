import textinput from '../text_input'
import LocalDatetime from '../local_datetime'

export default {
  name: 'ccpo-approval',

  components: {
    textinput,
    LocalDatetime
  },

  data: function () {
    return {
      approving: false,
      denying: false
    }
  },

  methods: {
    setReview: function (e) {
      if (e.target.value === 'approving') {
        this.approving = true
        this.denying = false
      } else {
        this.approving = false
        this.denying = true
      }
    },
  }
}
