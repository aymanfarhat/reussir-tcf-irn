export function useApi() {
  function apiOptions(options: Record<string, unknown> = {}) {
    const incomingHeaders = process.server ? useRequestHeaders(['cookie']) : {}
    const optionHeaders = (options.headers ?? {}) as Record<string, string>
    return {
      credentials: 'include' as const,
      ...options,
      headers: {
        ...incomingHeaders,
        ...optionHeaders,
      },
    }
  }

  async function get<T>(url: string, options: Record<string, unknown> = {}) {
    return await $fetch<T>(url, { method: 'GET', ...apiOptions(options) })
  }

  async function post<T>(url: string, body?: unknown, options: Record<string, unknown> = {}) {
    return await $fetch<T>(url, { method: 'POST', body, ...apiOptions(options) })
  }

  async function del<T>(url: string, options: Record<string, unknown> = {}) {
    return await $fetch<T>(url, { method: 'DELETE', ...apiOptions(options) })
  }

  return { get, post, del }
}
