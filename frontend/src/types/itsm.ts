/**
 * TypeScript types + Zod schemas untuk ITSM modules
 * State machine transitions di-mirror dari backend untuk UX feedback
 */
import { z } from 'zod'

// ── Status enums ──────────────────────────────────────────────
export const INCIDENT_STATUSES  = ['Open', 'In Progress', 'Resolved', 'Closed', 'Cancelled'] as const
export const INCIDENT_PRIORITIES = ['Low', 'Medium', 'High', 'Critical'] as const
export const INCIDENT_SEVERITIES = ['S1', 'S2', 'S3', 'S4'] as const

export const CHANGE_STATUSES    = ['Draft', 'Submitted', 'Approved', 'Rejected', 'In Progress', 'Completed', 'Cancelled'] as const
export const CHANGE_PRIORITIES  = ['Low', 'Medium', 'High', 'Critical'] as const
export const CHANGE_TYPES       = ['Standard', 'Normal', 'Emergency'] as const

export const PROBLEM_STATUSES   = ['Open', 'Under Investigation', 'Known Error', 'Resolved', 'Closed'] as const
export const REQUEST_STATUSES   = ['Draft', 'Submitted', 'Approved', 'Rejected', 'In Progress', 'Completed', 'Cancelled'] as const
export const REQUEST_PRIORITIES = ['Low', 'Medium', 'High'] as const
export const REQUEST_TYPES      = ['New Asset', 'Repair', 'Replacement', 'Software', 'Access', 'Other'] as const

// ── State machine (mirror dari backend) ──────────────────────
export const INCIDENT_TRANSITIONS: Record<string, string[]> = {
  'Open':        ['In Progress', 'Cancelled'],
  'In Progress': ['Resolved', 'Cancelled'],
  'Resolved':    ['Closed', 'Open'],
  'Closed':      [],
  'Cancelled':   [],
}

export const CHANGE_TRANSITIONS: Record<string, string[]> = {
  'Draft':       ['Submitted', 'Cancelled'],
  'Submitted':   ['Approved', 'Rejected', 'Cancelled'],
  'Approved':    ['In Progress', 'Cancelled'],
  'Rejected':    ['Draft'],
  'In Progress': ['Completed', 'Cancelled'],
  'Completed':   [],
  'Cancelled':   [],
}

export const PROBLEM_TRANSITIONS: Record<string, string[]> = {
  'Open':                ['Under Investigation', 'Closed'],
  'Under Investigation': ['Known Error', 'Resolved', 'Closed'],
  'Known Error':         ['Resolved', 'Closed'],
  'Resolved':            ['Closed', 'Open'],
  'Closed':              [],
}

export const REQUEST_TRANSITIONS: Record<string, string[]> = {
  'Draft':       ['Submitted', 'Cancelled'],
  'Submitted':   ['Approved', 'Rejected', 'Cancelled'],
  'Approved':    ['In Progress', 'Cancelled'],
  'Rejected':    ['Draft'],
  'In Progress': ['Completed', 'Cancelled'],
  'Completed':   [],
  'Cancelled':   [],
}

// ── Zod schemas ───────────────────────────────────────────────
export const IncidentSchema = z.object({
  title:           z.string().min(1, 'Title is required').max(200),
  description:     z.string().max(5000).optional(),
  priority:        z.enum(INCIDENT_PRIORITIES).default('Medium'),
  severity:        z.enum(INCIDENT_SEVERITIES).default('S3'),
  status:          z.enum(INCIDENT_STATUSES).default('Open'),
  asset_id:        z.number().int().positive().nullable().optional(),
  assigned_to:     z.number().int().positive().nullable().optional(),
  resolution_note: z.string().max(5000).optional(),
})

export const ChangeSchema = z.object({
  title:         z.string().min(1, 'Title is required').max(200),
  description:   z.string().max(5000).optional(),
  change_type:   z.enum(CHANGE_TYPES).default('Normal'),
  priority:      z.enum(CHANGE_PRIORITIES).default('Medium'),
  status:        z.enum(CHANGE_STATUSES).default('Draft'),
  asset_id:      z.number().int().positive().nullable().optional(),
  planned_start: z.string().optional(),
  planned_end:   z.string().optional(),
  rollback_plan: z.string().max(5000).optional(),
  notes:         z.string().max(5000).optional(),
})

export const ProblemSchema = z.object({
  title:       z.string().min(1, 'Title is required').max(200),
  description: z.string().max(5000).optional(),
  root_cause:  z.string().max(5000).optional(),
  workaround:  z.string().max(5000).optional(),
  status:      z.enum(PROBLEM_STATUSES).default('Open'),
  asset_id:    z.number().int().positive().nullable().optional(),
  assigned_to: z.number().int().positive().nullable().optional(),
})

export const RequestSchema = z.object({
  title:        z.string().min(1, 'Title is required').max(200),
  description:  z.string().max(5000).optional(),
  request_type: z.enum(REQUEST_TYPES).default('Other'),
  priority:     z.enum(REQUEST_PRIORITIES).default('Medium'),
  status:       z.enum(REQUEST_STATUSES).default('Draft'),
  asset_id:     z.number().int().positive().nullable().optional(),
  notes:        z.string().max(5000).optional(),
})

export type IncidentForm = z.infer<typeof IncidentSchema>
export type ChangeForm   = z.infer<typeof ChangeSchema>
export type ProblemForm  = z.infer<typeof ProblemSchema>
export type RequestForm  = z.infer<typeof RequestSchema>

// ── Badge color maps ──────────────────────────────────────────
export const STATUS_BADGE: Record<string, 'success' | 'info' | 'warning' | 'error' | 'neutral'> = {
  // Incident
  'Open':                  'error',
  'In Progress':           'warning',
  'Resolved':              'info',
  'Closed':                'success',
  'Cancelled':             'neutral',
  // Change/Request
  'Draft':                 'neutral',
  'Submitted':             'info',
  'Approved':              'success',
  'Rejected':              'error',
  'Completed':             'success',
  // Problem
  'Under Investigation':   'warning',
  'Known Error':           'error',
}

export const PRIORITY_BADGE: Record<string, 'success' | 'info' | 'warning' | 'error' | 'neutral'> = {
  'Low':      'neutral',
  'Medium':   'info',
  'High':     'warning',
  'Critical': 'error',
}
