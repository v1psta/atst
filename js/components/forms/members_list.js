import { compose, filter, equals, indexBy, partial, prop, pipe } from 'ramda'

const search = (query, members) => {
  if (query === '' || query === 'all') {
    return members
  } else {
    const normalizedQuery = query.toLowerCase()
    return members.filter(
      (member) => member.name.toLowerCase().includes(normalizedQuery)
    )
  }
}

const filterByStatus = (status, members) => {
  if (status === '' || status === 'all') {
    return members
  } else {
    return members.filter(
      (member) => member.status === status
    )
  }
}

const filterByRole = (role, rolesByDisplayname, members) => {
  const getRoleNameFromDisplayName = (_role) => rolesByDisplayname[_role].name

  if (role === '' || role === 'all') {
    return members
  } else {
    return members.filter(
      (member) => getRoleNameFromDisplayName(member.role) === role
    )
  }
}

export default {
  name: 'members-list',

  props: {
    members: Array,
    choices: Array,
  },

  data: function () {
    return {
      searchValue: '',
      status: '',
      role: '',
      rolesByDisplayName: indexBy(prop('display_name'), this.choices),
    }
  },

  computed: {
    searchedList: function () {
      return pipe(
        partial(search, [this.searchValue]),
        partial(filterByStatus, [this.status]),
        partial(filterByRole, [this.role, this.rolesByDisplayName]),
      )(this.members)
    }
  },
}
