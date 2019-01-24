import { shallowMount } from '@vue/test-utils'

import MembersList from '../members_list'

describe('MembersList', () => {
  const members = [
    {
      name: 'Luke Skywalker',
      num_env: 2,
      status: 'active',
      role: 'developer',
    },
    {
      name: 'Chewie',
      num_env: 3,
      status: 'pending',
      role: 'admin',
    },
  ]
  const role_choices = [
    { display_name: 'Developer', name: 'developer' },
    { display_name: 'Admin', name: 'admin' },
  ]
  const status_choices = [
    { display_name: 'Active', name: 'active' },
    { display_name: 'Pending', name: 'pending' },
  ]

  const createWrapper = () =>
    shallowMount(MembersList, {
      propsData: {
        members,
        role_choices,
        status_choices,
      },
    })

  it('should sort by name by default', () => {
    const wrapper = createWrapper()
    const listedMembers = wrapper.vm.searchedList
    const memberNames = listedMembers.map(member => member.name)
    expect(memberNames).toEqual(['Chewie', 'Luke Skywalker'])
  })

  it('should reverse sort by name when updated with Name', () => {
    const wrapper = createWrapper()
    wrapper.vm.updateSort('Name')
    const listedMembers = wrapper.vm.searchedList
    const memberNames = listedMembers.map(member => member.name)
    expect(memberNames).toEqual(['Luke Skywalker', 'Chewie'])
  })

  it('should sort by number of environments when environments selected', () => {
    const wrapper = createWrapper()
    wrapper.vm.updateSort('Environments')
    const listedMembers = wrapper.vm.searchedList
    const memberEnvs = listedMembers.map(member => member.num_env)
    expect(memberEnvs).toEqual([2, 3])
  })
})
