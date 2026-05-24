export default defineNuxtPlugin(async () => {
  await useSession().init()
})
