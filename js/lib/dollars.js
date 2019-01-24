export const formatDollars = (value, cents = true) => {
  if (typeof value === 'number') {
    return cents
      ? `$${value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`
      : `$${value.toFixed(0).replace(/\d(?=(\d{3})+(?!\d))/g, '$&,')}`
  }
  return ''
}

export const abbreviateDollars = (value, decimals = 1) => {
  if (value === null) {
    return null
  } // terminate early
  if (value === 0) {
    return '0'
  } // terminate early
  var b = value.toPrecision(2).split('e'), // get power
    k = b.length === 1 ? 0 : Math.floor(Math.min(b[1].slice(1), 14) / 3), // floor at decimals, ceiling at trillions
    c =
      k < 1
        ? value.toFixed(0 + decimals)
        : (value / Math.pow(10, k * 3)).toFixed(decimals), // divide by power
    d = c < 0 ? c : Math.abs(c), // enforce -0 is 0
    e = d + ['', 'k', 'M', 'B', 'T'][k] // append power
  return e
}
