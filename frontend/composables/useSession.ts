import type { AuthUser } from '~/types/api'

export function useSession() {
  const user = useState<AuthUser | null>('auth-user', () => null)
  const pending = useState<boolean>('auth-pending', () => false)
  const initialized = useState<boolean>('auth-initialized', () => false)

  const isLoggedIn = computed(() => Boolean(user.value))
  const api = useApi()

  async function ensureCsrf() {
    await api.get('/api/auth/csrf')
  }

  async function fetchSession() {
    pending.value = true
    try {
      user.value = await api.get<AuthUser>('/api/auth/me')
    } catch {
      user.value = null
    } finally {
      pending.value = false
      initialized.value = true
    }
  }

  async function init() {
    if (initialized.value) return
    await fetchSession()
  }

  async function login(username: string, password: string) {
    await ensureCsrf()
    await api.post('/api/auth/login', { username, password })
    await fetchSession()
  }

  async function signup(username: string, password: string, password2: string) {
    await ensureCsrf()
    await api.post('/api/auth/signup', { username, password, password2 })
    await fetchSession()
  }

  async function logout() {
    await ensureCsrf()
    await api.post('/api/auth/logout')
    user.value = null
    initialized.value = true
    await navigateTo('/login')
  }

  return { user, pending, initialized, isLoggedIn, init, fetchSession, login, signup, logout }
}
