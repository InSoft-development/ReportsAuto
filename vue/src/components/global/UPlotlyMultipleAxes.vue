<script>
import { ref, onMounted, toRef, watch, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../../stores/applicationStore'

import Plotly from '../local/Plotly.vue'

import { getAdditionalsSignals, updatePlotlyMultipleAxes } from '../../stores'

export default {
  name: 'UPlotlyMultipleAxex',
  components: { Plotly },
  props: {
    headerTitle: String(),
    mainSignal: {
      kks: String,
      description: String,
    },
    typeOfMainSignal: String,
    idPrefix: String,
    activeInterval: Number(),
    disabled: Boolean,
  },
  setup(props) {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    const { activeSignals, setActiveSignals } = applicationStore
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { object, group, intervals } = storeToRefs(applicationStore)

    // Реактивная ref ссылка на заголовок из пропа
    const headerTitleRef = toRef(props, 'headerTitle')
    // Реактивная ref ссылка на объект главного сигнала
    const mainSignalRef = toRef(props, 'mainSignal')
    // Реактивная ref ссылка на проп типа главного сигнала
    const typeOfMainSignalRef = toRef(props, 'typeOfMainSignal')
    // Реактивная ref ссылка на id для генерации чекбоксов
    const idPrefixRef = toRef(props, 'idPrefix')
    // Реактивная ref ссылка на номер интервала
    const activeIntervalRef = toRef(props, 'activeInterval')
    // Реактивная ref ссылка на отключение чекбоксов при построении отчета
    const disabledRef = toRef(props, 'disabled')

    // Массив объектов дополнительных датчиков
    const signals = ref([])
    // Массив выбранных чекбоксов датчиков
    const signalsCheckbox = ref([])

    // Показ спинера, если идет получение данных и рендеринг графика
    const loadStateInterval = ref(false)

    // данные для графика
    const dataMultipleAxes = ref([])
    // layout для графика
    const layoutMultipleAxes = ref({})

    const changeSignalCheckbox = async () => {
      loadStateInterval.value = true

      setActiveSignals(
        typeOfMainSignalRef.value,
        mainSignalRef.value.kks,
        [mainSignalRef.value.kks, ...signals.value.map(({ kks }) => kks)],
        signalsCheckbox.value,
      )

      await updatePlotlyMultipleAxes(
        dataMultipleAxes,
        layoutMultipleAxes,
        mainSignalRef,
        object,
        activeIntervalRef.value,
        signals,
        signalsCheckbox,
      )
      loadStateInterval.value = false
    }

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      loadStateInterval.value = true
      await getAdditionalsSignals(signals, mainSignalRef, object)
      signalsCheckbox.value = signals.value.map(({ kks }) => kks)
      signalsCheckbox.value.unshift(mainSignalRef.value.kks)
      setActiveSignals(
        typeOfMainSignalRef.value,
        mainSignalRef.value.kks,
        signalsCheckbox.value,
        signalsCheckbox.value,
      )

      await updatePlotlyMultipleAxes(
        dataMultipleAxes,
        layoutMultipleAxes,
        mainSignalRef,
        object,
        activeIntervalRef.value,
        signals,
        signalsCheckbox,
      )
      loadStateInterval.value = false
    })

    watch([object, group, intervals], async () => {
      loadStateInterval.value = true
      await getAdditionalsSignals(signals, mainSignalRef, object)
      signalsCheckbox.value = signals.value.map(({ kks }) => kks)
      signalsCheckbox.value.unshift(mainSignalRef.value.kks)
      loadStateInterval.value = false
    })

    onUnmounted(async () => {
      delete activeSignals[typeOfMainSignalRef.value][mainSignalRef.value.kks]
    })

    return {
      headerTitleRef,
      mainSignalRef,
      idPrefixRef,
      activeIntervalRef,
      disabledRef,
      signals,
      signalsCheckbox,
      loadStateInterval,
      dataMultipleAxes,
      layoutMultipleAxes,
      changeSignalCheckbox,
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
            <Plotly
              :data="dataMultipleAxes"
              :layout="layoutMultipleAxes"
            ></Plotly>
          </div>
        </div>
      </div>
    </div>
    <!--    <div class="container-fluid interval-multiple-axes-padding-signals">-->
    <div class="row">
      <div class="col">
        <Checkbox
          v-model="signalsCheckbox"
          :input-id="idPrefixRef + mainSignalRef.kks + '-Signals'"
          name="signalsCheckbox"
          :value="mainSignalRef.kks"
          @change="changeSignalCheckbox"
          :disabled="disabledRef"
        ></Checkbox>
        <label :for="idPrefixRef + mainSignalRef.kks + '-Signals'"
          >Основной сигнал:
          <span class="plotly-interval-header-title">{{
            mainSignalRef.kks + ' (' + mainSignalRef.description + ')'
          }}</span></label
        >
      </div>
    </div>
    <div class="row" v-for="signal in signals">
      <div class="col">
        <Checkbox
          v-model="signalsCheckbox"
          :input-id="idPrefixRef + signal.kks + '-Signals'"
          name="signalsCheckbox"
          :value="signal.kks"
          @change="changeSignalCheckbox"
          :disabled="disabledRef"
        ></Checkbox>
        <label :for="idPrefixRef + signal.kks + '-Signals'"
          >Дополнительный сигнал:
          <span :style="{ color: signal.color }">{{
            signal.kks + ' (' + signal.description + ')'
          }}</span></label
        >
      </div>
    </div>
  </div>
  <br />
  <!--  </div>-->
</template>

<style>
.plotly-interval-header-title {
  color: #1f77b4;
}
</style>
