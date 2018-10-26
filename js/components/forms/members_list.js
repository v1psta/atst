
export default {
  name: 'members-list',

  props: {
    members: Array,
  },

  data: function () {
    return {
      searchValue: '',
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
    },
  },
}
