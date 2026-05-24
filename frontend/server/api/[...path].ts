import { proxyToDjango } from '~/server/utils/djangoProxy'

export default defineEventHandler((event) => {
  const rawPath = event.context.params?.path ?? ''
  const path = Array.isArray(rawPath) ? rawPath.join('/') : rawPath
  const normalized = path.endsWith('/') ? path : `${path}/`
  return proxyToDjango(event, `/api/${normalized}`)
})
