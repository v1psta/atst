import { shallowMount } from '@vue/test-utils'

import RequestsList from '../requests_list'

describe('RequestsList', () => {

  describe('isExtended', () => {
    it('should disallow sorting if not extended', () => {
      const wrapper = shallowMount(RequestsList, { propsData: { isExtended: false } })
      expect(wrapper.vm.sort.columnName).toEqual('')
      wrapper.vm.updateSortValue('full_name')
      expect(wrapper.vm.sort.columnName).toEqual('')
    })

    it('should allow sorting when in extended mode', () => {
      const wrapper = shallowMount(RequestsList, { propsData: { isExtended: true } })
      expect(wrapper.vm.sort.columnName).toEqual('last_submission_timestamp')
      wrapper.vm.updateSortValue('full_name')
      expect(wrapper.vm.sort.columnName).toEqual('full_name')
    })
  })

  describe('sorting', () => {
    const requests = [{
      name: 'X Wing',
      last_edited_timestamp: 'Mon, 2 Jan 2017 12:34:56 GMT',
      last_submission_timestamp: 'Mon, 2 Jan 2017 12:34:56 GMT',
      full_name: 'Luke Skywalker',
      annual_usage: '80000',
      status: 'Approved',
      dod_component: 'Rebels'
    }, {
      name: 'TIE Fighter',
      last_edited_timestamp: 'Mon, 12 Nov 2018 12:34:56 GMT',
      last_submission_timestamp: 'Mon, 12 Nov 2018 12:34:56 GMT',
      full_name: 'Darth Vader',
      annual_usage: '999999',
      status: 'Approved',
      dod_component: 'Empire'
    }]

    const mountWrapper = () => shallowMount(RequestsList, { propsData: { requests, isExtended: true } })

    it('should default to sorting by submission recency', () => {
      const wrapper = mountWrapper()
      const displayedRequests = wrapper.vm.filteredRequests
      const requestNames = displayedRequests.map(req => req.name)
      expect(requestNames).toEqual(['TIE Fighter', 'X Wing'])
    })

    it('should reverse sort by submission time when selected', () => {
      const wrapper = mountWrapper()
      wrapper.vm.updateSortValue('last_submission_timestamp')
      const displayedRequests = wrapper.vm.filteredRequests
      const requestNames = displayedRequests.map(req => req.name)
      expect(requestNames).toEqual(['X Wing', 'TIE Fighter'])
    })

    it('handles sorting with un-submitted requests', () => {
      const unsubmittedRequest = {
        name: 'Death Star',
        status: 'Started',
        last_submission_timestamp: null
      }
      const wrapper = shallowMount(RequestsList, {
        propsData: {
          requests: [unsubmittedRequest, ...requests],
          isExtended: true
        }
      })
      const displayedRequests = wrapper.vm.filteredRequests
      expect(displayedRequests).toEqual([requests[1], requests[0], unsubmittedRequest])
    })
  })
})
