export interface AuthUser {
  id: number
  username: string
  displayName: string
  isStaff: boolean
  isSuperuser: boolean
}

export interface TestDefinition {
  id: number
  sourceId: string
  name: string
  mode: 'full' | 'oral' | 'written'
  description: string
}

export interface TaskDefinition {
  id: number
  sourceId: string
  taskNumber: number
  nameFr: string
  nameEn: string
  durationMinutes: number | null
  suggestedDurationMinutes: number | null
  durationSeconds: number
  wordCountMin: number | null
  wordCountMax: number | null
  expectedStructure: string[]
  requiredElements: string[]
  strategyTips: string[]
  commonPitfalls: string[]
  isWritten: boolean
  isOral: boolean
}

export interface Question {
  id: number
  sourceId: string
  sectionSourceId: 'expression_orale' | 'expression_ecrite'
  taskNumber: number
  taskTypeFr: string
  prompt: string
  themes: string[]
  timing: Record<string, unknown>
  addressee: string
  register: string
  channel: string
  examinerRoleFr: string
  expectedResponse: Record<string, any>
  evaluationFocus: string[]
  taskDefinition: TaskDefinition
}

export interface TaskGrade {
  id: number
  status: 'pending' | 'running' | 'succeeded' | 'failed'
  parsedResult: Record<string, any>
  audioFeedback: Record<string, any>
  audioFeedbackStatus: string
  audioFeedbackError: string
  improvedResponse: Record<string, any>
  improvedResponseStatus: string
  improvedResponseError: string
  overallScore20: number | null
  estimatedCefrLevel: string
  automaticFailure: boolean
  automaticFailureReasons: string[]
  errorMessage: string
}

export interface TaskAttempt {
  id: number
  uuid: string
  testSessionUuid: string
  sequenceOrder: number
  status: string
  startedAt: string | null
  deadlineAt: string | null
  submittedAt: string | null
  submittedLate: boolean
  answerText: string
  transcriptText: string
  manualTranscript: boolean
  audioFileUrl: string
  audioMimeType: string
  wordCountObserved: number | null
  withinWordLimits: boolean | null
  isWritten: boolean
  isOral: boolean
  candidateText: string
  question: Question
  grade: TaskGrade | null
}

export interface TestSession {
  id: number
  uuid: string
  mode: string
  status: string
  startedAt: string | null
  completedAt: string | null
  currentStepOrder: number
  oralScore: number | null
  oralLevel: string
  writtenScore: number | null
  writtenLevel: string
  metadata: Record<string, any>
  testDefinition: TestDefinition
  attempts: TaskAttempt[]
  createdAt: string
  updatedAt: string
}

export interface AttemptDetailResponse {
  session: TestSession
  attempt: TaskAttempt
  attempts: TaskAttempt[]
  nextAttemptOrder: number | null
}

export interface TaskFeedbackResponse {
  session: TestSession
  attempt: TaskAttempt
  grade: TaskGrade | null
  nextAttempt: TaskAttempt | null
  exampleResponses: { label: string; answer: string }[]
  personalBestAttempt: TaskAttempt | null
}
