
export default {
  name: 'members-list',

  props: {
    members: Array,
  },

  data: function () {
    return {
      searchValue: '',
      status: '',
      role: '',
    }
  },

  computed: {
    searchedList: function () {
      return this.members.filter(
        member => this.status ?
          member.status === this.status | this.status === 'all'
          : true
      ).filter(
        member => this.role ?
          member.role.toLowerCase() === this.role | this.role === 'all'
          : true
      ).filter(
        member => this.searchValue ? member.name.toLowerCase()
          .includes(this.searchValue.toLowerCase()) : true
      )
    }
  },
}
