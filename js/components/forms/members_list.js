
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

  mounted: function () {
    // this.searchedList = this.members
  },

  computed: {
    searchedList: function () {
      return this.members.filter(
        member => this.status ? member.status === this.status : true
      ).filter(
          member => this.role ? member.role.toLowerCase() === this.role : true
      ).filter(
        member => this.searchValue ? member.name.toLowerCase()
          .includes(this.searchValue.toLowerCase()) : true
      )
    }
  },

  // watch: {
  //   status: function (status) {
  //     this.searchedList = this.searchedList.filter(
  //       member => member.status === status
  //     )
  //   },
  //   role: function (role) {
  //     this.searchedList = this.searchedList.filter(
  //       member => member.role.toLowerCase() === role
  //     )
  //   }
  // },

  methods: {
    search: function () {
      console.log("search")
    },
  },
}
