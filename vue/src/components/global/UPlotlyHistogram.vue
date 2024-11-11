<script>
import { ref, onMounted, toRef, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../../stores/applicationStore'

import Plotly from '../local/Plotly.vue'

import { updatePlotlyHistogram } from '../../stores'

export default {
  name: 'UPlotlyHistogram',
  components: { Plotly },
  props: {
    headerTitle: String(),
  },
  setup(props) {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { object, group, intervals } = storeToRefs(applicationStore)

    // Реактивная ref ссылка на заголовок из пропа
    const headerTitleRef = toRef(props, 'headerTitle')

    // Показ спинера, если идет получение данных и рендеринг графика
    const loadStateHistogram = ref(false)

    // данные для графика
    const dataHistogram = ref([])
    // layout для графика
    const layoutHistogram = ref({})

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      loadStateHistogram.value = true
      await updatePlotlyHistogram(dataHistogram, layoutHistogram)
      loadStateHistogram.value = false
    })

    watch([object, group, intervals], async () => {
      loadStateHistogram.value = true
      await updatePlotlyHistogram(dataHistogram, layoutHistogram)
      loadStateHistogram.value = false
    })

    return {
      headerTitleRef,
      loadStateHistogram,
      dataHistogram,
      layoutHistogram,
    }
  },
}
</script>

<template>
  <div>
    <h3 class="plotly-interval-header-title">{{ headerTitleRef }}</h3>
    <div class="card d-flex align-items-center justify-content-center">
      <div class="container-fluid">
        <div class="row position-absolute top-50 start-50 translate-middle z-1">
          <div class="col">
            <ProgressSpinner
              v-if="loadStateHistogram"
              class="z-2"
              stroke-width="5"
              animation-duration=".3s"
              fill="var(--surface-ground)"
              :style="{ width: '100px', height: '100px' }"
            >
            </ProgressSpinner>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <Plotly :data="dataHistogram" :layout="layoutHistogram"></Plotly>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.plotly-interval-header-title {
  color: #1f77b4;
}
</style>
