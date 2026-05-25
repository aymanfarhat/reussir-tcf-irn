const CIRCUMFERENCE = 2 * Math.PI * 26

export function useExamScoring() {
  const { t } = useI18n()

  function scorePercent(score: number | null | undefined): number {
    if (score === null || score === undefined) return 0
    return Math.max(0, Math.min(100, (Number(score) / 20) * 100))
  }

  function arcDash(score: number | null | undefined): string {
    const filled = (scorePercent(score) / 100) * CIRCUMFERENCE
    return `${filled} ${CIRCUMFERENCE - filled}`
  }

  function tierColor(score: number | null | undefined): string {
    const value = Number(score ?? 0)
    if (value >= 16) return '#65a30d'
    if (value >= 12) return '#4f46e5'
    if (value >= 8) return '#d97706'
    return '#dc2626'
  }

  function tierLabel(score: number | null | undefined): string {
    const value = Number(score ?? 0)
    if (value >= 16) return t('scoreTiers.strong')
    if (value >= 12) return t('scoreTiers.ready')
    if (value >= 8) return t('scoreTiers.developing')
    return t('scoreTiers.needsWork')
  }

  return { CIRCUMFERENCE, arcDash, tierColor, tierLabel, scorePercent }
}
