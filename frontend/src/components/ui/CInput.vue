<script setup lang="ts">
/**
 * CInput — IBM Carbon text input
 * - Background surface-1, 0px radius, bottom-border focus treatment
 * - Security: v-model binding only, no v-html, no innerHTML
 * - Accessibility: label + id association, aria-describedby for errors
 */
import { computed, useId } from 'vue'

const props = withDefaults(defineProps<{
  modelValue?:  string
  label?:       string
  placeholder?: string
  type?:        string
  error?:       string
  helperText?:  string
  disabled?:    boolean
  required?:    boolean
  id?:          string
  autocomplete?: string
}>(), {
  modelValue:   '',
  type:         'text',
  disabled:     false,
  required:     false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// Generate unique ID if not provided — accessibility requirement
const uid = useId()
const inputId    = computed(() => props.id || `input-${uid}`)
const helperId   = computed(() => `${inputId.value}-helper`)
const errorId    = computed(() => `${inputId.value}-error`)

const hasError   = computed(() => !!props.error)
const describedBy = computed(() => {
  const ids = []
  if (props.helperText) ids.push(helperId.value)
  if (hasError.value)   ids.push(errorId.value)
  return ids.join(' ') || undefined
})
</script>

<template>
  <div class="flex flex-col gap-xs w-full">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="type-body-sm text-ink font-medium"
    >
      {{ label }}
      <span v-if="required" class="text-error ml-xxs" aria-hidden="true">*</span>
    </label>

    <!-- Input wrapper — Carbon bottom-border focus treatment -->
    <div class="relative">
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        :aria-describedby="describedBy"
        :aria-invalid="hasError || undefined"
        :aria-required="required || undefined"
        class="
          w-full bg-surface-1 text-ink type-body-sm
          h-9 px-sm
          rounded-none
          border-0 border-b border-hairline
          focus:border-b-2 focus:border-primary
          disabled:opacity-40 disabled:cursor-not-allowed
          placeholder:text-ink-subtle
          transition-colors duration-100
          outline-none
        "
        :class="{
          'border-b-2 border-error': hasError,
        }"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <!-- Helper text -->
    <p
      v-if="helperText && !hasError"
      :id="helperId"
      class="type-caption text-ink-muted"
    >
      {{ helperText }}
    </p>

    <!-- Error message -->
    <p
      v-if="hasError"
      :id="errorId"
      role="alert"
      class="type-caption text-error"
    >
      {{ error }}
    </p>
  </div>
</template>
