type FlashKind = 'info' | 'success' | 'warning' | 'error'

interface FlashMessage {
  text: string
  kind: FlashKind
}

export function useFlash() {
  const flash = useState<FlashMessage | null>('flash-message', () => null)

  function show(text: string, kind: FlashKind = 'info') {
    flash.value = { text, kind }
  }

  function clear() {
    flash.value = null
  }

  return { flash, show, clear }
}
