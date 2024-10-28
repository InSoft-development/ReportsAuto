<script>
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  setup() {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { sidebarWidth } = storeToRefs(applicationStore)
    return {
      sidebarWidth,
    }
  },
}
</script>

<template>
  <div :style="{ padding: `0px 20px 0px 20px` }">
    <UPlotlyInterval
      :headerTitle="'График вероятности наступления аномалии за весь период'"
    ></UPlotlyInterval>
  </div>
</template>

<style></style>
