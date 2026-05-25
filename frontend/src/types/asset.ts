/**
 * TypeScript types untuk Asset module
 * Zod schema digunakan untuk runtime validation di form
 */
import { z } from 'zod'

// ── Zod schema — validasi sisi klien sebelum kirim ke API ─────
export const AssetSchema = z.object({
  asset_tag: z
    .string()
    .min(1, 'Asset tag is required')
    .max(50, 'Max 50 characters')
    .regex(/^[A-Za-z0-9\-_]+$/, 'Only alphanumeric, dash, underscore'),
  serial_number: z
    .string()
    .min(1, 'Serial number is required')
    .max(100, 'Max 100 characters'),
  po_number: z
    .string()
    .max(100, 'Max 100 characters')
    .nullable()
    .optional(),
  model_id: z
    .number({ required_error: 'Model is required' })
    .int()
    .positive(),
  location_id: z
    .number({ required_error: 'Location is required' })
    .int()
    .positive(),
  employee_id: z
    .number()
    .int()
    .positive()
    .nullable()
    .optional(),
  status: z.enum(['Active', 'Available', 'Repair', 'Disposed']).default('Available'),
  purchase_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format: YYYY-MM-DD')
    .nullable()
    .optional(),
  warranty_months: z
    .number()
    .int()
    .min(0)
    .max(600)
    .nullable()
    .optional(),
  os_license: z
    .string()
    .max(100)
    .nullable()
    .optional(),
  notes: z
    .string()
    .max(2000)
    .nullable()
    .optional(),
})

export type AssetFormData = z.infer<typeof AssetSchema>

// ── API response types ────────────────────────────────────────
export interface Asset extends AssetFormData {
  id:         number
  created_at: string
  updated_at: string
  model?:     { id: number; name: string; brand?: { id: number; name: string } | null; category?: { id: number; name: string } | null } | null
  location?:  { id: number; name: string } | null
  employee?:  { id: number; name: string; department: number | null } | null
  network?:   { ip_address: string | null; mac_address: string | null; hostname: string | null; vlan: string | null } | null
}

export interface AssetFilters {
  page?:       number
  perPage?:    number
  status?:     string
  search?:     string
  locationId?: number
  categoryId?: number
}

export interface PaginatedResponse<T> {
  data:     T[]
  total:    number
  page:     number
  per_page: number
  pages:    number
}

export const ASSET_STATUS_OPTIONS = [
  { value: 'Active',    label: 'Active' },
  { value: 'Available', label: 'Available' },
  { value: 'Repair',    label: 'Under Repair' },
  { value: 'Disposed',  label: 'Disposed' },
] as const

export const STATUS_BADGE_MAP: Record<string, 'success' | 'info' | 'warning' | 'error' | 'neutral'> = {
  Active:    'success',
  Available: 'info',
  Repair:    'warning',
  Disposed:  'neutral',
}
