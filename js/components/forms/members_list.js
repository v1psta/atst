
export default {
  name: 'members-list',

  template: '#search-template',

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
    // console.log(this.members)
  },

  methods: {
    search: function () {
      console.log(this.members)
      this.searchedList = this.members.filter(member => member.name.includes(this.searchValue))
      console.log(this.searchedList)
    },
  },
}
