import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import emailMask from 'text-mask-addons/dist/emailMask'
import createAutoCorrectedDatePipe from 'text-mask-addons/dist/createAutoCorrectedDatePipe'

export default {
  anything: {
    mask: false,
    match: /\s*/,
    unmask: [],
    validationError: 'Please enter a response',
  },
  requiredField: {
    mask: false,
    match: /.+/,
    unmask: [],
    validationError: 'This field is required',
  },
  integer: {
    mask: createNumberMask({ prefix: '', allowDecimal: false }),
    match: /^[1-9]\d*$/,
    unmask: [','],
    validationError: 'Please enter a number',
  },
  dollars: {
    mask: createNumberMask({ prefix: '$', allowDecimal: true }),
    match: /^-?\d+\.?\d*$/,
    unmask: ['$', ','],
    validationError: 'Please enter a dollar amount',
  },
  gigabytes: {
    mask: createNumberMask({ prefix: '', suffix: ' GB', allowDecimal: false }),
    match: /^[1-9]\d*$/,
    unmask: [',', ' GB'],
    validationError: 'Please enter an amount of data in gigabytes',
  },
  email: {
    mask: emailMask,
    match: /(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/i,
    unmask: [],
    validationError: 'Please enter a valid e-mail address',
  },
  date: {
    mask: [/\d/, /\d/, '/', /\d/, /\d/, '/', /\d/, /\d/, /\d/, /\d/],
    match: /(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d/,
    unmask: [],
    pipe: createAutoCorrectedDatePipe('mm/dd/yyyy HH:MM'),
    keepCharPositions: true,
    validationError: 'Please enter a valid date in the form MM/DD/YYYY',
  },
  usPhone: {
    mask: [
      '(',
      /[1-9]/,
      /\d/,
      /\d/,
      ')',
      ' ',
      /\d/,
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      /\d/,
      /\d/,
    ],
    match: /^\d{10}$/,
    unmask: ['(', ')', '-', ' '],
    validationError: 'Please enter a 10-digit phone number',
  },
  phoneExt: {
    mask: createNumberMask({
      prefix: '',
      allowDecimal: false,
      integerLimit: 10,
      allowLeadingZeroes: true,
      includeThousandsSeparator: false,
    }),
    match: /^\d{0,10}$/,
    unmask: [],
    validationError: 'Optional: Please enter up to 10 digits',
  },
  dodId: {
    mask: createNumberMask({
      prefix: '',
      allowDecimal: false,
      allowLeadingZeroes: true,
      includeThousandsSeparator: false,
    }),
    match: /^\d{10}$/,
    unmask: [],
    validationError: 'Please enter a 10-digit DoD ID number',
  },
  peNumber: {
    mask: false,
    match: /(0\d)(0\d)(\d{3})([a-z,A-Z]{1,3})/,
    unmask: ['_'],
    validationError:
      'Please enter a valid PE number. Note that it should be 7 digits followed by 1-3 letters, and should have a zero as the first and third digits.',
  },
  treasuryCode: {
    mask: createNumberMask({
      prefix: '',
      allowDecimal: false,
      allowLeadingZeroes: true,
      includeThousandsSeparator: false,
    }),
    match: /^0*([1-9]{4}|[1-9]{6})$/,
    unmask: [],
    validationError:
      'Please enter a valid Program Treasury Code. Note that it should be a four digit or six digit number, optionally prefixed by one or more zeros.',
  },
  baCode: {
    mask: false,
    match: /[0-9]{2}\w?$/,
    unmask: [],
    validationError:
      'Please enter a valid BA Code. Note that it should be two digits, followed by an optional letter.',
  },
  portfolioName: {
    mask: false,
    match: /^.{4,100}$/,
    unmask: [],
    validationError:
      'Portfolio names must be at least 4 and not more than 100 characters',
  },
}
