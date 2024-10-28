<script>
import { ref, onMounted, toRef, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { newPlot } from 'plotly.js-dist'

import { useApplicationStore } from '../../stores/applicationStore'

export default {
  name: 'Plotly',
  props: {
    data: Object(),
    layout: Object(),
  },
  setup(props) {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { object, group, collapsed } = storeToRefs(applicationStore)

    // Ref-ссылка на div блок с Plotly
    const plotly = ref(null)
    // Конфиг графика Plotly
    const plotlyConfig = {
      scrollZoom: true,
      displayModeBar: false,
      responsive: true,
    }
    // Ссылка на проп данных для графика для сохранениея реактивности
    const dataRef = toRef(props, 'data')
    // Ссылка на проп layout для графика для сохранениея реактивности
    const layoutRef = toRef(props, 'layout')

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      newPlot(plotly.value, dataRef.value, layoutRef.value, plotlyConfig)
    })

    watch([dataRef, layoutRef, collapsed], () => {
      newPlot(plotly.value, dataRef.value, layoutRef.value, plotlyConfig)
    })

    return {
      plotly,
    }
  },
}
</script>
<template>
  <div ref="plotly"></div>
</template>
<style></style>
