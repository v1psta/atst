import Modal from '../../mixins/modal'
import LocalDatetime from '../../components/local_datetime'
import { formatDollars } from '../../lib/dollars'
import { parse } from 'date-fns'
import { compose, partial, indexBy, prop, sortBy, reverse, pipe } from 'ramda'

export default {
    name: 'requests-list',

    mixins: [Modal],

    components: {
      Modal,
      LocalDatetime
    },

    props: {
      requests: {
        type: Array,
        default: [],
      },
      isExtended: {
        type: Boolean,
        default: false,
      },
      statuses: {
        type: Array,
        default: [],
      },
    },

    data: function () {
      const defaultSort = (sort, requests) => sortBy(prop(sort.columnName), requests)
      const dateSort = (sort, requests) => {
        const parseDate = compose(partial(parse), prop(sort.columnName))
        return sortBy(parseDate, requests)
      }

      const columnList = [
        { displayName: 'JEDI Cloud Request Name', attr: 'name', sortFunc: defaultSort },
        { displayName: 'Date Request Submitted', attr: 'last_submission_timestamp', sortFunc: dateSort },
        { displayName: 'Date Request Last Edited', attr: 'last_edited_timestamp', extendedOnly: true, sortFunc: dateSort },
        { displayName: 'Requester', attr: 'full_name', extendedOnly: true, sortFunc: defaultSort, },
        { displayName: 'Projected Annual Usage ($)', attr: 'annual_usage', sortFunc: defaultSort },
        { displayName: 'Request Status', attr: 'status', sortFunc: defaultSort },
        { displayName: 'DOD Component', attr: 'dod_component', extendedOnly: true, sortFunc: defaultSort },
      ]

      return {
        searchValue: '',
        statusValue: '',
        sort: {
          columnName: '',
          isAscending: true
        },
        columns: indexBy(prop('attr'), columnList),
      }
    },

    mounted: function () {
    },

    computed: {
      filteredRequests: function () {
        return pipe(
          partial(this.applySearch, [this.searchValue]),
          partial(this.applyFilters, [this.statusValue]),
          partial(this.applySort, [this.sort]),
        )(this.requests)
      }
    },

    methods: {
      getColumns: function() {
        return Object.values(this.columns)
          .filter((column) => !column.extendedOnly || this.isExtended)
      },
      applySearch: (query, requests) => {
        return requests.filter(
          (request) => query !== '' ?
            request.name.toLowerCase().includes(query.toLowerCase()) :
            true
        )
      },
      applyFilters: (status, requests) => {
        return requests.filter(
          (request) => status !== '' ?
            request.status === status :
            true
        )
      },
      applySort: function(sort, requests) {
        if (sort.columnName === '') {
          return requests
        } else {
          const { sortFunc } = this.columns[sort.columnName]
          const sorted = sortFunc(sort, requests)
          return sort.isAscending ?
            sorted :
            reverse(sorted)
        }
      },
      dollars: (value) => formatDollars(value, false),
      updateSortValue: function(columnName) {
        if (columnName === this.sort.columnName) {
          this.sort.isAscending = !this.sort.isAscending
        }
        this.sort.columnName = columnName;
      },
    },
  }
