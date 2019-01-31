import { shallowMount } from '@vue/test-utils'

import EditOfficerForm from '../edit_officer_form'

describe('EditOfficerForm', () => {
  it('defaults to not editing', () => {
    const wrapper = shallowMount(EditOfficerForm)
    expect(wrapper.vm.$data.editing).toEqual(false)
  })

  it('does not start in editing mode when no errors', () => {
    const wrapper = shallowMount(EditOfficerForm, {
      propsData: { hasErrors: false },
    })
    expect(wrapper.vm.$data.editing).toEqual(false)
  })

  it('does start in editing mode when the form has errors', () => {
    const wrapper = shallowMount(EditOfficerForm, {
      propsData: { hasErrors: true },
    })
    expect(wrapper.vm.$data.editing).toEqual(true)
  })

  it('does start in editing mode when the form has changes', () => {
    const wrapper = shallowMount(EditOfficerForm, {
      propsData: { hasChanges: true },
    })
    expect(wrapper.vm.$data.editing).toEqual(true)
  })

  it('starts editing when edit method called', () => {
    const wrapper = shallowMount(EditOfficerForm)
    wrapper.vm.edit({ preventDefault: () => null })
    expect(wrapper.vm.$data.editing).toEqual(true)
  })

  it('stops editing when cancel method called', () => {
    const wrapper = shallowMount(EditOfficerForm)
    wrapper.vm.cancel()
    expect(wrapper.vm.$data.editing).toEqual(false)
  })
})
