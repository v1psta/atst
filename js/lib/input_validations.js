import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import emailMask from 'text-mask-addons/dist/emailMask'

export default {
  anything: {
    mask: false,
    match: /^(?!\s*$).+/,
    unmask: [],
  },
  dollars: {
    mask: createNumberMask({ prefix: '$', allowDecimal: true }),
    match: /^-?\d+\.?\d*$/,
    unmask: ['$',',']
  },
  email: {
    mask: emailMask,
    match: /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
    unmask: [],
  }
}
