import { compose, sortBy, reverse, indexBy, partial, prop, pipe, toLower } from 'ramda'

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

const filterByStatus = (status, statusesByDisplayName, members) => {
  const getStatusFromDisplayName = (_status) => statusesByDisplayName[_status].name

  if (status === '' || status === 'all') {
    return members
  } else {
    return members.filter(
      (member) => getStatusFromDisplayName(member.status) === status
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

const sort = (sortInfo, members) => {
  if (sortInfo.columnName === '') {
    return members
  } else {
    const sortColumn = sortInfo.columns[sortInfo.columnName]
    const sortedMembers = sortColumn.sortFunc(sortColumn.attr, members)

    return sortInfo.isAscending ?
      sortedMembers :
      reverse(sortedMembers)
    }
}

export default {
  name: 'members-list',

  props: {
    members: Array,
    role_choices: Array,
    status_choices: Array,
  },

  data: function () {
    const alphabeticalSort = (attr, members) => {
      const lowercaseProp = compose(toLower, prop(attr))
      return sortBy(lowercaseProp, members)
    }

    const numericSort = (attr, members) => sortBy(prop(attr), members)

    const columns = [
      {
        displayName: 'Name',
        attr: 'name',
        sortFunc: alphabeticalSort,
        width: "50%"
      },
      {
        displayName: 'Environments',
        attr: 'num_env',
        sortFunc: numericSort,
        class: "table-cell--align-right"
      },
      {
        displayName: 'Status',
        attr: 'status',
        sortFunc: alphabeticalSort
      },
      {
        displayName: 'Workspace Role',
        attr: 'role',
        sortFunc: alphabeticalSort
      },
    ]

    return {
      searchValue: '',
      status: '',
      statusesByDisplayName: indexBy(prop('display_name'), this.status_choices),
      role: '',
      rolesByDisplayName: indexBy(prop('display_name'), this.role_choices),
      sortInfo: {
        columnName: '',
        isAscending: true,
        columns: indexBy(prop('displayName'), columns)
      },
    }
  },

  computed: {
    searchedList: function () {
      return pipe(
        partial(search, [this.searchValue]),
        partial(filterByStatus, [this.status, this.statusesByDisplayName]),
        partial(filterByRole, [this.role, this.rolesByDisplayName]),
        partial(sort, [this.sortInfo])
      )(this.members)
    }
  },

  methods: {
    updateSort: function(columnName) {
      // clicking a column twice toggles ascending / descending
      if (columnName === this.sortInfo.columnName) {
        this.sortInfo.isAscending = !this.sortInfo.isAscending
      }

      this.sortInfo.columnName = columnName
    },
    getColumns: function() {
      return Object.values(this.sortInfo.columns)
    }
  }
}
