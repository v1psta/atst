import checkboxinput from './checkbox_input'
import FormMixin from '../mixins/form'

export default {
  name: 'fullpagenotice',

  mixins: [FormMixin],

  components: {
    checkboxinput,
  },

  data: function() {
    return {
      agree: false,
      visible: true,
    }
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleValidChange)
  },

  methods: {
    handleValidChange: function(event) {
      this.agree = event.value
    },

    agreeToTermsClick: function() {
      this.visible = false
    },
  },
}
