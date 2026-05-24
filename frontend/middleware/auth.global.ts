export default defineNuxtRouteMiddleware(async (to) => {
  const { init, isLoggedIn } = useSession()
  await init()
  const requiresAuth = to.meta.requires === 'auth'
  if (requiresAuth && !isLoggedIn.value) {
    return navigateTo(`/login?returnTo=${encodeURIComponent(to.fullPath)}`)
  }
})
