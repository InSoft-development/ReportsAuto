<script>
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../stores/applicationStore'


export default {
    setup(){
        // Определение текущего URL
        const route = useRoute()
        const currentRoute = computed(() => route.path)
        // Из URL достаем номер интервала для передачи пропа в компонент UPlotlyInterval
        const activeInterval = computed(() => {
          return Number(route.params.intervalsId)
        })

        return {
          currentRoute,
          activeInterval
        }
    }
}

</script>

<template>
    <div :style="{ 'padding': '0px 20px 0px 20px' }">
        <UPlotlyInterval
          :headerTitle="'График вероятности наступления аномалии за весь период'"
          :activeInterval="activeInterval"
        ></UPlotlyInterval>
  </div>
</template>

<style></style>
