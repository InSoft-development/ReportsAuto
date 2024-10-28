<script>
import { ref, reactive, computed, onMounted, toRef, toRefs, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../../stores/applicationStore'

import Plotly from '../local/Plotly.vue'

import { updatePlotlyInterval } from '../../stores'

export default {
  name: 'UPlotlyInterval',
  components: { Plotly },
  props: {
    headerTitle: String(),
    activeInterval: Number()
  },
  setup(props, context) {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { object, group, intervals } = storeToRefs(applicationStore)

    // Реактивная ref ссылка на заголовок из пропа
    const headerTitleRef = toRef(props, 'headerTitle')
    // Реактивная ref ссылка на номер интервала
    const activeIntervalRef = toRef(props, 'activeInterval')

    // Показ спинера, если идет получение данных и рендеринг графика
    const loadStateInterval = ref(false)

    // данные для графика
    const dataInterval = ref([])
    // layout для графика
    const layoutInterval = ref({})

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      loadStateInterval.value = true
      await updatePlotlyInterval(dataInterval, layoutInterval, object, group, activeIntervalRef.value)
      loadStateInterval.value = false
    })

    watch([object, group, intervals, activeIntervalRef], async () => {
      loadStateInterval.value = true
      await updatePlotlyInterval(dataInterval, layoutInterval, object, group, activeIntervalRef.value)
      loadStateInterval.value = false
    })

    return {
      headerTitleRef,
      loadStateInterval,
      dataInterval,
      layoutInterval,
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
              v-if="loadStateInterval"
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
            <Plotly :data="dataInterval" :layout="layoutInterval"></Plotly>
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
