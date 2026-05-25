export function useUiLabels() {
  const { locale, t, te } = useI18n()

  function enumLabel(group: string, value?: string | null): string {
    if (!value) return ''
    const normalized = value.toLowerCase().replace(/[^a-z0-9]+/g, '_')
    const key = `${group}.${normalized}`
    return te(key) ? t(key) : value
  }

  function formatDateTime(value?: string | null): string {
    if (!value) return ''
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return new Intl.DateTimeFormat(locale.value === 'fr' ? 'fr-FR' : 'en-US', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date)
  }

  function modeLabel(value?: string | null): string {
    return enumLabel('modes', value)
  }

  function statusLabel(value?: string | null): string {
    return enumLabel('statuses', value)
  }

  function gradeStatusLabel(value?: string | null): string {
    return enumLabel('gradeStatuses', value)
  }

  function taskLabel(taskNumber?: number | string | null): string {
    return t('common.taskNumber', { number: taskNumber ?? '-' })
  }

  return { enumLabel, formatDateTime, gradeStatusLabel, modeLabel, statusLabel, taskLabel }
}
