/**
 * Unit tests: types/asset.ts
 * Test Zod schema validation untuk Asset form.
 */
import { describe, it, expect } from 'vitest'
import { AssetSchema, ASSET_STATUS_OPTIONS, STATUS_BADGE_MAP } from '@/types/asset'

describe('AssetSchema', () => {
  const validData = {
    asset_tag:     'SRV-0001',
    serial_number: 'SN-123456',
    model_id:      1,
    location_id:   1,
    status:        'Available' as const,
  }

  it('accepts valid data', () => {
    const result = AssetSchema.safeParse(validData)
    expect(result.success).toBe(true)
  })

  it('rejects empty asset_tag', () => {
    const result = AssetSchema.safeParse({ ...validData, asset_tag: '' })
    expect(result.success).toBe(false)
  })

  it('rejects empty serial_number', () => {
    const result = AssetSchema.safeParse({ ...validData, serial_number: '' })
    expect(result.success).toBe(false)
  })

  it('rejects invalid model_id (non-positive)', () => {
    const result = AssetSchema.safeParse({ ...validData, model_id: 0 })
    expect(result.success).toBe(false)
  })

  it('rejects invalid location_id', () => {
    const result = AssetSchema.safeParse({ ...validData, location_id: -1 })
    expect(result.success).toBe(false)
  })

  it('rejects invalid status', () => {
    const result = AssetSchema.safeParse({ ...validData, status: 'InvalidStatus' })
    expect(result.success).toBe(false)
  })

  it('accepts all valid statuses', () => {
    const statuses = ['Active', 'Available', 'Repair', 'Disposed']
    statuses.forEach(status => {
      const result = AssetSchema.safeParse({ ...validData, status })
      expect(result.success).toBe(true)
    })
  })

  it('accepts optional fields as undefined', () => {
    const result = AssetSchema.safeParse({
      ...validData,
      po_number:       undefined,
      employee_id:     undefined,
      purchase_date:   undefined,
      warranty_months: undefined,
      os_license:      undefined,
      notes:           undefined,
    })
    expect(result.success).toBe(true)
  })

  it('rejects negative warranty_months', () => {
    const result = AssetSchema.safeParse({ ...validData, warranty_months: -1 })
    expect(result.success).toBe(false)
  })

  it('accepts warranty_months 0 (no warranty)', () => {
    const result = AssetSchema.safeParse({ ...validData, warranty_months: 0 })
    expect(result.success).toBe(true)
  })
})

describe('ASSET_STATUS_OPTIONS', () => {
  it('contains all 4 statuses', () => {
    const values = ASSET_STATUS_OPTIONS.map(o => o.value)
    expect(values).toContain('Active')
    expect(values).toContain('Available')
    expect(values).toContain('Repair')
    expect(values).toContain('Disposed')
  })

  it('each option has value and label', () => {
    ASSET_STATUS_OPTIONS.forEach(opt => {
      expect(opt.value).toBeTruthy()
      expect(opt.label).toBeTruthy()
    })
  })
})

describe('STATUS_BADGE_MAP', () => {
  it('Active maps to success', () => {
    expect(STATUS_BADGE_MAP['Active']).toBe('success')
  })

  it('Available maps to info', () => {
    expect(STATUS_BADGE_MAP['Available']).toBe('info')
  })

  it('Repair maps to warning', () => {
    expect(STATUS_BADGE_MAP['Repair']).toBe('warning')
  })

  it('Disposed maps to neutral', () => {
    expect(STATUS_BADGE_MAP['Disposed']).toBe('neutral')
  })
})
