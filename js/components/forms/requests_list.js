import Modal from '../../mixins/modal'
import LocalDatetime from '../../components/local_datetime'
import { formatDollars } from '../../lib/dollars'

export default {
    name: 'requests-list',

    mixins: [Modal],

    components: {
      Modal,
      LocalDatetime
    },

    props: {
      initialData: {
        type: Array,
        default: [],
      },
      isExtended: {
        type: Boolean,
        default: false,
      },
    },

    data: function () {
      const requests = this.initialData
      return {
        requests,
        searchValue: '',
        statusValue: '',
      }
    },

    mounted: function () {
    },

    computed: {
      filteredRequests: function () {
        return this.applyFilters(this.applySearch(this.requests, this.searchValue), this.statusValue)
      }
    },

    methods: {
      applySearch: (requests, query) => {
        return requests.filter(
          (request) => query !== '' ?
            request.name.toLowerCase().includes(query.toLowerCase()) :
            true
        )
      },
      applyFilters: (requests, status) => {
        return requests.filter(
          (request) => status !== '' ?
            request.simple_status.toLowerCase() === status :
            true
        )
      },
      dollars: (value) => formatDollars(value, false),
    },
  }
