<script setup lang="ts">
import { Construction } from '@lucide/vue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const route = useRoute()
const { t } = useI18n()
const title = computed(() => t(String(route.meta.titleKey ?? 'navigation.dashboard')))
</script>

<template>
  <section class="content-panel min-h-96">
    <div class="grid min-h-96 place-items-center p-8 text-center">
      <div>
        <span class="mx-auto grid size-12 place-items-center rounded-md bg-slate-100 text-slate-600">
          <Construction :size="24" />
        </span>
        <h2 class="mt-4 text-xl font-extrabold text-slate-950">{{ title }}</h2>
        <p class="mt-2 text-sm text-slate-500">{{ t('common.soon') }}</p>
      </div>
    </div>
  </section>
</template>

