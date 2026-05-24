import type { H3Event } from 'h3'
import {
  appendResponseHeader,
  getMethod,
  getQuery,
  getRequestHeader,
  readBody,
  readMultipartFormData,
  setHeader,
  setResponseStatus,
  useRuntimeConfig,
} from '#imports'

function parseCsrfFromCookieHeader(cookieHeader: string | undefined): string | null {
  if (!cookieHeader) return null
  const match = cookieHeader.split(/;\s*/).find((part) => part.startsWith('csrftoken='))
  return match ? decodeURIComponent(match.split('=')[1] ?? '') : null
}

function toCamel(value: string): string {
  return value.replace(/_([a-z0-9])/g, (_, letter: string) => letter.toUpperCase())
}

function toSnake(value: string): string {
  return value.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
}

export function camelize<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => camelize(item)) as T
  if (value && typeof value === 'object' && !(value instanceof Date)) {
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [toCamel(key), camelize(entry)]),
    ) as T
  }
  return value
}

export function snakeize<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => snakeize(item)) as T
  if (value && typeof value === 'object' && !(value instanceof Date) && !(value instanceof File)) {
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [toSnake(key), snakeize(entry)]),
    ) as T
  }
  return value
}

async function readRequestBody(event: H3Event, contentType: string): Promise<BodyInit | undefined> {
  const method = getMethod(event)
  if (method === 'GET' || method === 'HEAD') return undefined

  if (contentType.includes('multipart/form-data')) {
    const parts = await readMultipartFormData(event)
    const formData = new FormData()
    for (const part of parts ?? []) {
      if (part.filename) {
        const blob = new Blob([part.data], { type: part.type || 'application/octet-stream' })
        formData.append(part.name ?? 'file', blob, part.filename)
      } else {
        formData.append(part.name ?? 'field', part.data.toString())
      }
    }
    return formData
  }

  const body = await readBody(event)
  return JSON.stringify(snakeize(body ?? {}))
}

export async function proxyToDjango(event: H3Event, djangoPath: string): Promise<unknown> {
  const config = useRuntimeConfig()
  const base = config.djangoInternalBase as string
  const method = getMethod(event)
  const cookie = getRequestHeader(event, 'cookie') ?? ''
  const csrf = parseCsrfFromCookieHeader(cookie)
  const contentType = getRequestHeader(event, 'content-type') ?? ''

  const headers: HeadersInit = {
    accept: getRequestHeader(event, 'accept') ?? 'application/json',
    cookie,
  }
  if (method !== 'GET' && method !== 'HEAD' && !contentType.includes('multipart/form-data')) {
    headers['content-type'] = 'application/json'
  }
  if (method !== 'GET' && method !== 'HEAD' && csrf) {
    headers['x-csrftoken'] = csrf
  }

  const url = new URL(djangoPath, base)
  for (const [key, value] of Object.entries(getQuery(event))) {
    if (Array.isArray(value)) {
      for (const item of value) url.searchParams.append(key, String(item))
    } else if (value !== undefined) {
      url.searchParams.set(key, String(value))
    }
  }

  const response = await fetch(url, {
    method,
    headers,
    body: await readRequestBody(event, contentType),
    redirect: 'manual',
  })

  setResponseStatus(event, response.status)
  for (const setCookie of response.headers.getSetCookie?.() ?? []) {
    appendResponseHeader(event, 'set-cookie', setCookie)
  }

  const responseType = response.headers.get('content-type') ?? ''
  const cacheControl = response.headers.get('cache-control')
  if (cacheControl) setHeader(event, 'cache-control', cacheControl)

  if (responseType.includes('application/json')) {
    const data = await response.json()
    return camelize(data)
  }

  const location = response.headers.get('location')
  if (location) setHeader(event, 'location', location)
  if (responseType) setHeader(event, 'content-type', responseType)
  return new Uint8Array(await response.arrayBuffer())
}
