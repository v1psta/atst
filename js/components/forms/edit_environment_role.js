import FormMixin from '../../mixins/form'
import Modal from '../../mixins/modal'

// Note: If refactoring consider using nested vue components as suggested by Dan:
// https://github.com/dod-ccpo/atst/pull/799/files#r282240663
// May also want to reconsider the data structure by storing the roles and members separately

export const NO_ACCESS = 'No Access'

export const EditEnvironmentRole = {
  name: 'edit-environment-role',

  mixins: [FormMixin],

  props: {
    initialRoleCategories: Array,
  },

  data: function() {
    return {
      selectedSection: null,
      roleCategories: this.sanitizeValues(this.initialRoleCategories),
    }
  },

  methods: {
    sanitizeValues: function(roles) {
      roles.forEach(role => {
        role.members.forEach(member => {
          if (member.role_name === null) {
            member.role_name = NO_ACCESS
          }
        })
      })
      return roles
    },

    checkNoAccess: function(role) {
      return role === NO_ACCESS
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
      for (let role of this.roleCategories) {
        for (let member of role.members) {
          if (member.user_id === userId) {
            return member
          }
        }
      }
    },

    removeUser: function(userId) {
      for (let role of this.roleCategories) {
        role.members = role.members.filter(member => {
          return member.user_id !== userId
        })
        if (!role.members) {
          role.members = []
        }
      }
    },

    addUser: function(userInfo, newRole) {
      this.roleCategories.forEach(role => {
        if (role.role === newRole) {
          userInfo.role_name = newRole
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
