import { shallowMount } from '@vue/test-utils'

import ConfirmationPopover from '../confirmation_popover'


describe('ConfirmationPopover', () => {
  it('matches snapshot', () => {
    const wrapper = shallowMount(ConfirmationPopover, {
      propsData: {
        action: '/some-url',
        btn_text: 'Do something dangerous',
        cancel_btn_text: 'Cancel',
        confirm_btn_text: 'Confirm',
        confirm_msg: 'Are you sure you want to do that?',
        csrf_token: '42'
      }
    })

    expect(wrapper).toMatchSnapshot()
  })
})

