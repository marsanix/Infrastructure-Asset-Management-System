/**
 * Unit tests: useForm composable
 * Test Zod validation, setField, reset, handleSubmit.
 */
import { describe, it, expect, vi } from 'vitest'
import { z } from 'zod'
import { useForm } from '@/composables/useForm'

const TestSchema = z.object({
  name:  z.string().min(1, 'Name is required').max(50),
  email: z.string().email('Invalid email'),
  age:   z.number().int().min(0).optional(),
})
type TestForm = z.infer<typeof TestSchema>

describe('useForm', () => {
  describe('initial state', () => {
    it('values initialized with initialValues', () => {
      const { values } = useForm<TestForm>(TestSchema, { name: 'Alice' })
      expect(values.name).toBe('Alice')
    })

    it('errors empty on init', () => {
      const { errors } = useForm<TestForm>(TestSchema)
      expect(Object.keys(errors)).toHaveLength(0)
    })

    it('submitting false on init', () => {
      const { submitting } = useForm<TestForm>(TestSchema)
      expect(submitting.value).toBe(false)
    })
  })

  describe('setField', () => {
    it('updates value', () => {
      const { values, setField } = useForm<TestForm>(TestSchema)
      setField('name', 'Bob')
      expect(values.name).toBe('Bob')
    })

    it('sets touched for field', () => {
      const { touched, setField } = useForm<TestForm>(TestSchema)
      setField('name', 'Bob')
      expect(touched.name).toBe(true)
    })

    it('clears error when valid value set', () => {
      const { errors, setField } = useForm<TestForm>(TestSchema, { email: 'not-email' })
      setField('email', 'not-email')
      // Trigger validation
      setField('email', 'valid@test.com')
      expect(errors.email).toBeUndefined()
    })

    it('sets error when invalid value set', () => {
      const { errors, setField } = useForm<TestForm>(TestSchema)
      setField('email', 'not-an-email')
      expect(errors.email).toBeTruthy()
    })
  })

  describe('validate', () => {
    it('returns false for invalid form', () => {
      const { validate } = useForm<TestForm>(TestSchema, { name: '' })
      expect(validate()).toBe(false)
    })

    it('returns true for valid form', () => {
      const { validate } = useForm<TestForm>(TestSchema, {
        name: 'Valid Name',
        email: 'valid@test.com',
      })
      expect(validate()).toBe(true)
    })

    it('populates errors on invalid form', () => {
      const { validate, errors } = useForm<TestForm>(TestSchema, {
        name: '',
        email: 'bad-email',
      })
      validate()
      expect(errors.name).toBeTruthy()
      expect(errors.email).toBeTruthy()
    })

    it('clears errors on re-validate when valid', () => {
      const { validate, errors, setField } = useForm<TestForm>(TestSchema, {
        name: '',
        email: 'bad',
      })
      validate()
      expect(errors.name).toBeTruthy()

      setField('name', 'Valid')
      setField('email', 'valid@test.com')
      validate()
      expect(errors.name).toBeUndefined()
      expect(errors.email).toBeUndefined()
    })
  })

  describe('reset', () => {
    it('resets values to initial', () => {
      const { values, setField, reset } = useForm<TestForm>(TestSchema, { name: 'Init' })
      setField('name', 'Changed')
      reset()
      expect(values.name).toBe('Init')
    })

    it('resets with new values', () => {
      const { values, reset } = useForm<TestForm>(TestSchema, { name: 'Init' })
      reset({ name: 'NewDefault', email: 'new@test.com' })
      expect(values.name).toBe('NewDefault')
      expect(values.email).toBe('new@test.com')
    })

    it('clears errors on reset', () => {
      const { validate, errors, reset } = useForm<TestForm>(TestSchema, { name: '' })
      validate()
      expect(errors.name).toBeTruthy()
      reset()
      expect(errors.name).toBeUndefined()
    })

    it('clears touched on reset', () => {
      const { touched, setField, reset } = useForm<TestForm>(TestSchema)
      setField('name', 'x')
      expect(touched.name).toBe(true)
      reset()
      expect(touched.name).toBeUndefined()
    })
  })

  describe('handleSubmit', () => {
    it('calls onValid with parsed data when valid', async () => {
      const onValid = vi.fn()
      const { setField, handleSubmit } = useForm<TestForm>(TestSchema)
      setField('name', 'Alice')
      setField('email', 'alice@test.com')
      await handleSubmit(onValid)
      expect(onValid).toHaveBeenCalledOnce()
      expect(onValid.mock.calls[0][0]).toMatchObject({ name: 'Alice', email: 'alice@test.com' })
    })

    it('does NOT call onValid when invalid', async () => {
      const onValid = vi.fn()
      const { handleSubmit } = useForm<TestForm>(TestSchema, { name: '' })
      await handleSubmit(onValid)
      expect(onValid).not.toHaveBeenCalled()
    })

    it('sets submitting to false after submit', async () => {
      const { submitting, setField, handleSubmit } = useForm<TestForm>(TestSchema)
      setField('name', 'Bob')
      setField('email', 'bob@test.com')
      await handleSubmit(vi.fn())
      expect(submitting.value).toBe(false)
    })

    it('sets submitting to false even if onValid throws', async () => {
      const { submitting, setField, handleSubmit } = useForm<TestForm>(TestSchema)
      setField('name', 'Bob')
      setField('email', 'bob@test.com')
      const throwing = vi.fn().mockRejectedValue(new Error('fail'))
      try {
        await handleSubmit(throwing)
      } catch {
        // expected
      }
      expect(submitting.value).toBe(false)
    })
  })
})
