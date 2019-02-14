import ToggleMixin from '../mixins/toggle'

export default {
  name: 'toggler',

  mixins: [ToggleMixin],

  props: {
    defaultVisible: {
      type: Boolean,
      default: () => false,
    },
  },
}
