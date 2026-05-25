/**
 * useForm — generic form composable dengan Zod validation
 * Digunakan di semua form IAMS untuk konsistensi validasi
 */
import { ref, reactive } from 'vue'
import type { ZodSchema, ZodError } from 'zod'

export function useForm<T extends Record<string, unknown>>(
  schema: ZodSchema<T>,
  initialValues: Partial<T> = {}
) {
  const values  = reactive<Partial<T>>({ ...initialValues })
  const errors  = reactive<Partial<Record<keyof T, string>>>({})
  const touched = reactive<Partial<Record<keyof T, boolean>>>({})
  const submitting = ref(false)

  function validate(): boolean {
    // Clear errors
    Object.keys(errors).forEach(k => delete (errors as Record<string, unknown>)[k])

    const result = schema.safeParse(values)
    if (!result.success) {
      const zodErr = result.error as ZodError
      zodErr.errors.forEach(e => {
        const field = e.path[0] as keyof T
        if (field && !errors[field]) {
          (errors as Record<string, string>)[field as string] = e.message
        }
      })
      return false
    }
    return true
  }

  function setField<K extends keyof T>(key: K, value: T[K]) {
    (values as Record<string, unknown>)[key as string] = value
    ;(touched as Record<string, boolean>)[key as string] = true
    // Validate field on change
    const result = schema.safeParse(values)
    if (!result.success) {
      const fieldErr = result.error.errors.find(e => e.path[0] === key)
      if (fieldErr) {
        (errors as Record<string, string>)[key as string] = fieldErr.message
      } else {
        delete (errors as Record<string, unknown>)[key as string]
      }
    } else {
      delete (errors as Record<string, unknown>)[key as string]
    }
  }

  function reset(newValues: Partial<T> = {}) {
    Object.keys(values).forEach(k => delete (values as Record<string, unknown>)[k])
    Object.assign(values, { ...initialValues, ...newValues })
    Object.keys(errors).forEach(k => delete (errors as Record<string, unknown>)[k])
    Object.keys(touched).forEach(k => delete (touched as Record<string, unknown>)[k])
  }

  async function handleSubmit(onValid: (data: T) => Promise<void> | void) {
    if (!validate()) return
    submitting.value = true
    try {
      const parsed = schema.parse(values)
      await onValid(parsed)
    } finally {
      submitting.value = false
    }
  }

  return { values, errors, touched, submitting, validate, setField, reset, handleSubmit }
}
