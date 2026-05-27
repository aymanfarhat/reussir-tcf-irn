import type { TaskAttempt, TestSession } from '~/types/api'

const DONE_ATTEMPT_STATUSES = new Set(['submitted', 'graded', 'grading_failed'])

export interface SessionSummary {
  totalTasks: number
  completedTasks: number
  gradedTasks: number
  oralTasks: number
  writtenTasks: number
  oralCompletedTasks: number
  writtenCompletedTasks: number
  averageScore: number | null
  bestScore: number | null
  scoreLevel: string
  sections: Array<'oral' | 'written'>
  taskNumbers: number[]
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function roundScore(value: number): number {
  return Math.round(value * 10) / 10
}

function isAttemptCompleted(attempt: TaskAttempt): boolean {
  return Boolean(attempt.submittedAt || DONE_ATTEMPT_STATUSES.has(attempt.status))
}

function attemptScore(attempt: TaskAttempt): number | null {
  const score = attempt.grade?.overallScore20
  return attempt.grade?.status === 'succeeded' && isNumber(score) ? score : null
}

export function summarizeSession(session: TestSession): SessionSummary {
  const attempts = session.attempts ?? []
  const completedAttempts = attempts.filter(isAttemptCompleted)
  const gradedScores = attempts.map(attemptScore).filter(isNumber)
  const sectionScores = [session.oralScore, session.writtenScore].filter(isNumber)
  const scoreSource = gradedScores.length > 0 ? gradedScores : sectionScores
  const averageScore = scoreSource.length > 0 ? roundScore(scoreSource.reduce((total, score) => total + score, 0) / scoreSource.length) : null
  const bestScore = scoreSource.length > 0 ? Math.max(...scoreSource) : null
  const oralTasks = attempts.filter((attempt) => attempt.isOral).length
  const writtenTasks = attempts.filter((attempt) => attempt.isWritten).length
  const sections: Array<'oral' | 'written'> = []

  if (oralTasks > 0 || isNumber(session.oralScore)) sections.push('oral')
  if (writtenTasks > 0 || isNumber(session.writtenScore)) sections.push('written')

  return {
    totalTasks: attempts.length,
    completedTasks: completedAttempts.length,
    gradedTasks: gradedScores.length,
    oralTasks,
    writtenTasks,
    oralCompletedTasks: completedAttempts.filter((attempt) => attempt.isOral).length,
    writtenCompletedTasks: completedAttempts.filter((attempt) => attempt.isWritten).length,
    averageScore,
    bestScore,
    scoreLevel: session.mode === 'oral' ? session.oralLevel : session.mode === 'written' ? session.writtenLevel : '',
    sections,
    taskNumbers: [...new Set(attempts.map((attempt) => attempt.question.taskNumber))].sort((first, second) => first - second),
  }
}

export function formatSessionScore(score: number | null): string {
  return score === null ? '-' : score.toFixed(1).replace('.0', '')
}
