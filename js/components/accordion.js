import ToggleMixin from '../mixins/toggle'

export default {
  name: 'accordion',

  mixins: [ToggleMixin],

  props: {
    defaultVisible: {
      type: Boolean,
      default: false,
    },
  },
}
