<script setup lang="ts">
/**
 * CSelect — Carbon select dropdown
 * Accessibility: label + id, aria-invalid, aria-describedby
 */
import { computed, useId } from 'vue'

interface Option {
  value: string | number
  label: string
  disabled?: boolean
}

const props = withDefaults(defineProps<{
  modelValue?: string | number
  label?:      string
  options?:    Option[]
  placeholder?: string
  error?:      string
  disabled?:   boolean
  required?:   boolean
  id?:         string
}>(), {
  options:  () => [],
  disabled: false,
  required: false,
})

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const uid     = useId()
const inputId = computed(() => props.id || `select-${uid}`)
const errorId = computed(() => `${inputId.value}-error`)
const hasError = computed(() => !!props.error)
</script>

<template>
  <div class="flex flex-col gap-xs w-full">
    <label v-if="label" :for="inputId" class="type-body-sm text-ink font-medium">
      {{ label }}
      <span v-if="required" class="text-error ml-xxs" aria-hidden="true">*</span>
    </label>

    <select
      :id="inputId"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :aria-invalid="hasError || undefined"
      :aria-describedby="hasError ? errorId : undefined"
      class="
        w-full bg-surface-1 text-ink type-body-sm
        h-9 px-sm
        rounded-none
        border-0 border-b border-hairline
        focus:border-b-2 focus:border-primary
        disabled:opacity-40 disabled:cursor-not-allowed
        outline-none appearance-none
        transition-colors duration-100
        cursor-pointer
      "
      :class="{ 'border-b-2 border-error': hasError }"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option v-if="placeholder" value="" disabled :selected="!modelValue">
        {{ placeholder }}
      </option>
      <option
        v-for="opt in options"
        :key="opt.value"
        :value="opt.value"
        :disabled="opt.disabled"
      >
        {{ opt.label }}
      </option>
    </select>

    <p v-if="hasError" :id="errorId" role="alert" class="type-caption text-error">
      {{ error }}
    </p>
  </div>
</template>
