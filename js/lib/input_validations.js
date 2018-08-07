export default {
  anything: {
    mask: [],
    unmask: null,
    match: /^(?!\s*$).+/
  },
  dollars: {
    mask: ['$','/^\d+/','.','/^\d+/'],
    unmask: ['$',','],
    match: /^-?\d+\.?\d*$/
  }
}
