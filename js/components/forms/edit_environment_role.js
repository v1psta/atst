import FormMixin from '../../mixins/form'
import Modal from '../../mixins/modal'

// Note: If refactoring consider using nested vue components as suggested by Dan:
// https://github.com/dod-ccpo/atst/pull/799/files#r282240663
// May also want to reconsider the data structure by storing the roles and members separately

export default {
  name: 'edit-environment-role',

  mixins: [FormMixin],

  props: {
    initialRoles: Array,
  },

  data: function() {
    return {
      selectedSection: null,
      roles: this.sanitizeValues(this.initialRoles),
    }
  },

  methods: {
    sanitizeValues: function(roles) {
      roles.forEach(role => {
        role.members.forEach(member => {
          if (member.role === null) {
            member.role = 'no_access'
          }
        })
      })
      return roles
    },

    checkNoAccess: function(role) {
      return role === 'no_access'
    },

    toggleSection: function(sectionName) {
      if (this.selectedSection === sectionName) {
        this.selectedSection = null
      } else {
        this.selectedSection = sectionName
      }
    },

    onInput: function(e) {
      this.changed = true
      this.updateRoles(e.target.attributes['user-id'].value, e.target.value)
      this.showError = false
      this.showValid = true
    },

    getUserInfo: function(userId) {
      for (let role of this.roles) {
        for (let member of role.members) {
          if (member.user_id === userId) {
            return member
          }
        }
      }
    },

    removeUser: function(userId) {
      for (let role of this.roles) {
        role.members = role.members.filter(member => {
          return member.user_id !== userId
        })
        if (!role.members) {
          role.members = []
        }
      }
    },

    addUser: function(userInfo, newRole) {
      this.roles.forEach(role => {
        if (role.role === newRole) {
          userInfo.role = newRole
          role.members.push(userInfo)
        }
      })
    },

    updateRoles: function(userId, newRole) {
      var userInfo = this.getUserInfo(userId)
      this.removeUser(userId)
      this.addUser(userInfo, newRole)
      this.toggleSection()
    },
  },

  render: function(createElement) {
    return createElement('p', 'Please implement inline-template')
  },
}
