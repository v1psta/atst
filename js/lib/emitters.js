export const emitEvent = (event_type, el, data) => {
  el.$root.$emit(event_type, {
    ...data,
    parent_uid: el.$parent && el.$parent._uid,
  })
}
