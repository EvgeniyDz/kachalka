<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppNavigation from '@/components/AppNavigation.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-100 text-slate-900">
    <AppNavigation />
    <div class="lg:pl-64">
      <AppHeader />
      <main class="mx-auto w-full max-w-7xl p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
