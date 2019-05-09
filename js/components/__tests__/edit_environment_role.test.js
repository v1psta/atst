import { shallowMount } from '@vue/test-utils'
import EditEnvironmentRole from '../forms/edit_environment_role'

describe('EditEnvironmentRole', () => {
  var initialRoles, wrapper

  beforeEach(() => {
    initialRoles = [
      {
        role: 'no_access',
        members: [
          { role: null, user_id: '123' },
          { role: null, user_id: '456' },
        ],
      },
      {
        role: 'Basic Access',
        members: [{ role: 'Basic Access', user_id: '789' }],
      },
      {
        role: 'Network Admin',
        members: [],
      },
      {
        role: 'Business Read-only',
        members: [
          { role: 'Business Read-only', user_id: '012' },
          { role: 'Business Read-only', user_id: '345' },
        ],
      },
      {
        role: 'Technical Read-only',
        members: [{ role: 'Technical Read-only', user_id: '678' }],
      },
    ]

    wrapper = shallowMount(EditEnvironmentRole, { propsData: { initialRoles } })
  })

  it('removes null roles to no_access', () => {
    let roles = wrapper.vm.sanitizeValues([
      { role: 'no_access', members: [{ role: null }] },
    ])
    expect(roles).toEqual([
      { role: 'no_access', members: [{ role: 'no_access' }] },
    ])
  })

  it('gets the data for a user', () => {
    let member_data = wrapper.vm.getUserInfo('678')

    expect(member_data).toEqual({ role: 'Technical Read-only', user_id: '678' })
  })

  it('removes a user from role', () => {
    let techRole = wrapper.vm.roles.find(role => {
      return role.role === 'Technical Read-only'
    })

    expect(techRole.members.length).toEqual(1)
    wrapper.vm.removeUser('678')
    expect(techRole.members.length).toEqual(0)
  })

  it('adds user to a role', () => {
    let techRole = wrapper.vm.roles.find(role => {
      return role.role === 'Technical Read-only'
    })

    expect(techRole.members.length).toEqual(1)
    wrapper.vm.addUser({ user_id: '901' }, 'Technical Read-only')
    expect(techRole.members.length).toEqual(2)
  })

  it('updates users role', () => {
    let techRole = wrapper.vm.roles.find(role => {
      return role.role === 'Technical Read-only'
    })
    let businessRole = wrapper.vm.roles.find(role => {
      return role.role === 'Business Read-only'
    })

    expect(techRole.members.length).toEqual(1)
    expect(businessRole.members.length).toEqual(2)
    wrapper.vm.updateRoles('678', 'Business Read-only')
    expect(techRole.members.length).toEqual(0)
    expect(businessRole.members.length).toEqual(3)
  })
})
