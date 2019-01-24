import { createLocalVue, shallowMount } from '@vue/test-utils'
import VTooltip from 'v-tooltip'

import ConfirmationPopover from '../confirmation_popover'

const localVue = createLocalVue()
localVue.use(VTooltip)

describe('ConfirmationPopover', () => {
  const wrapper = shallowMount(ConfirmationPopover, {
    localVue,
    propsData: {
      action: '/some-url',
      btn_text: 'Do something dangerous',
      cancel_btn_text: 'Cancel',
      confirm_btn_text: 'Confirm',
      confirm_msg: 'Are you sure you want to do that?',
      csrf_token: '42',
    },
  })

  it('matches snapshot', () => {
    expect(wrapper).toMatchSnapshot()
  })

  it('renders form with hidden csrf input', () => {
    const input = wrapper.find('input[type=hidden]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('value')).toBe('42')
  })
})
