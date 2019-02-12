import ToggleMixin from '../mixins/toggle'

const cookieName = 'expandSidenav'

export default {
  name: 'sidenav-toggler',

  mixins: [ToggleMixin],

  props: {
    defaultVisible: {
      type: Boolean,
      default: function() {
        if (document.cookie.match(cookieName)) {
          return !!document.cookie.match(cookieName + ' *= *true')
        } else {
          return true
        }
      },
    },
  },

  methods: {
    toggle: function(e) {
      e.preventDefault()
      this.isVisible = !this.isVisible
      document.cookie = cookieName + '=' + this.isVisible + '; path=/'
    },
  },
}
