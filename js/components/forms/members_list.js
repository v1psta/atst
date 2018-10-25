
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
      searchedList: [],
    }
  },

  mounted: function () {
    this.searchedList = this.members
  },

  methods: {
    search: function () {
      this.searchedList = this.members.filter(
        member => member.name.toLowerCase()
        .includes(this.searchValue.toLowerCase())
      )

      if (this.status) {
        this.searchedList = this.searchedList.filter(
          member => member.status === this.status
        )
      }

      if (this.role) {
        this.searchedList = this.searchedList.filter(
            member => member.role.toLowerCase() === this.role
        )
      }
    },
  },
}
