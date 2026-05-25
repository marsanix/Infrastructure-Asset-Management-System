/**
 * Unit tests: ITSM state machine mirror di frontend (types/itsm.ts)
 * Memastikan transisi yang valid/invalid sesuai dengan backend.
 */
import { describe, it, expect } from 'vitest'
import {
  INCIDENT_TRANSITIONS,
  CHANGE_TRANSITIONS,
  PROBLEM_TRANSITIONS,
  REQUEST_TRANSITIONS,
  STATUS_BADGE,
  PRIORITY_BADGE,
} from '@/types/itsm'

describe('ITSM State Machine (frontend mirror)', () => {
  describe('INCIDENT_TRANSITIONS', () => {
    it('Open dapat ke In Progress', () => {
      expect(INCIDENT_TRANSITIONS['Open']).toContain('In Progress')
    })
    it('Open dapat ke Cancelled', () => {
      expect(INCIDENT_TRANSITIONS['Open']).toContain('Cancelled')
    })
    it('Closed adalah terminal state (kosong)', () => {
      expect(INCIDENT_TRANSITIONS['Closed']).toHaveLength(0)
    })
    it('Resolved dapat re-open ke Open', () => {
      expect(INCIDENT_TRANSITIONS['Resolved']).toContain('Open')
    })
  })

  describe('CHANGE_TRANSITIONS', () => {
    it('Draft → Submitted valid', () => {
      expect(CHANGE_TRANSITIONS['Draft']).toContain('Submitted')
    })
    it('Completed adalah terminal state', () => {
      expect(CHANGE_TRANSITIONS['Completed']).toHaveLength(0)
    })
    it('Rejected dapat kembali ke Draft', () => {
      expect(CHANGE_TRANSITIONS['Rejected']).toContain('Draft')
    })
  })

  describe('PROBLEM_TRANSITIONS', () => {
    it('Open → Under Investigation valid', () => {
      expect(PROBLEM_TRANSITIONS['Open']).toContain('Under Investigation')
    })
    it('Closed adalah terminal state', () => {
      expect(PROBLEM_TRANSITIONS['Closed']).toHaveLength(0)
    })
  })

  describe('REQUEST_TRANSITIONS', () => {
    it('Draft → Submitted valid', () => {
      expect(REQUEST_TRANSITIONS['Draft']).toContain('Submitted')
    })
    it('Completed adalah terminal state', () => {
      expect(REQUEST_TRANSITIONS['Completed']).toHaveLength(0)
    })
  })
})

describe('STATUS_BADGE mapping', () => {
  it('Open mapped ke error variant', () => {
    expect(STATUS_BADGE['Open']).toBe('error')
  })
  it('Closed mapped ke success', () => {
    expect(STATUS_BADGE['Closed']).toBe('success')
  })
  it('Resolved mapped ke info', () => {
    expect(STATUS_BADGE['Resolved']).toBe('info')
  })
  it('In Progress mapped ke warning', () => {
    expect(STATUS_BADGE['In Progress']).toBe('warning')
  })
  it('Cancelled mapped ke neutral', () => {
    expect(STATUS_BADGE['Cancelled']).toBe('neutral')
  })
  it('Approved mapped ke success', () => {
    expect(STATUS_BADGE['Approved']).toBe('success')
  })
})

describe('PRIORITY_BADGE mapping', () => {
  it('Critical mapped ke error', () => {
    expect(PRIORITY_BADGE['Critical']).toBe('error')
  })
  it('High mapped ke warning', () => {
    expect(PRIORITY_BADGE['High']).toBe('warning')
  })
  it('Low mapped ke neutral', () => {
    expect(PRIORITY_BADGE['Low']).toBe('neutral')
  })
})
