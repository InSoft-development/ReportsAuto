<script>
import { useRoute } from 'vue-router'
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../stores/applicationStore'

import { getTopAndOtherGroupSignals, startIntervalReport } from '../stores'

import { socket } from '../socket'
import axios from 'axios'

export default {
  setup() {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    const { activeSignals } = applicationStore
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { object, group, intervals, loadStateSidebar } =
      storeToRefs(applicationStore)
    // Определение текущего URL
    const route = useRoute()
    const currentRoute = computed(() => route.path)
    // Из URL достаем номер интервала для передачи пропа в компонент UPlotlyInterval
    const activeInterval = computed(() => {
      return Number(route.params.intervalsId)
    })
    // Из интервалов достаем по ключу title лейбел интервала
    const activeIntervalLabel = computed(() => {
      if (intervals.value.length) {
        return intervals.value[activeInterval.value].title
      }
      return ''
    })

    // Массив объектов чекбоксов датчиков, внесших максимальный вклад в аномалию группы
    const topGroupSignals = ref([])
    const topCheckbox = ref([])
    // Массив объектов чекбоксов остальных датчиков группы
    const otherGroupSignals = ref([])
    const otherCheckbox = ref([])

    // Процент построения отчета по интервалу
    const percentIntervalReport = ref(0)
    // Флаг показа ProgressBar
    const intervalReportActive = ref(false)

    // Нажатие на кнопку построения отчета на интервале
    const onIntervalReportButtonClick = async () => {
      percentIntervalReport.value = 0
      loadStateSidebar.value = true
      intervalReportActive.value = true
      let status = await startIntervalReport(
        object,
        group,
        activeInterval,
        topGroupSignals,
        otherGroupSignals,
        activeSignals,
      )

      if (status !== 'error') {
        // Загрузка файла html
        const URL = window.api.url
        // Загрузка файла html
        const linkCommonReportHtml = document.createElement('a')
        linkCommonReportHtml.download = `interval_report_${object.value}_group_${group.value}_${activeIntervalLabel.value}.html`

        await axios
          .get(URL + '/interval_report.html', {
            params: {
              objectSelected: object.value,
              activeInterval: activeInterval.value,
            },
          })
          .then(res => {
            linkCommonReportHtml.href = window.URL.createObjectURL(
              new Blob([res.data], { type: 'text/html' }),
            )
            linkCommonReportHtml.click()
            linkCommonReportHtml.remove()
            window.URL.revokeObjectURL(linkCommonReportHtml.href)
          })
          .catch(error => {
            console.log(error)
          })

        // Загрузка файла pdf
        const linkCommonReportPdf = document.createElement('a')
        linkCommonReportPdf.download = `interval_report_${object.value}_group_${group.value}_${activeIntervalLabel.value}.pdf`

        await axios
          .get(URL + '/interval_report.pdf', {
            params: {
              objectSelected: object.value,
              activeInterval: activeInterval.value,
            },
            responseType: 'blob',
          })
          .then(res => {
            linkCommonReportPdf.href = window.URL.createObjectURL(
              new Blob([res.data], { type: 'text/html' }),
            )
            linkCommonReportPdf.click()
            linkCommonReportPdf.remove()
            window.URL.revokeObjectURL(linkCommonReportPdf.href)
          })
          .catch(error => {
            console.log(error)
          })
      }
      percentIntervalReport.value = 100
      intervalReportActive.value = false

      loadStateSidebar.value = false
    }

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      await getTopAndOtherGroupSignals(
        topGroupSignals,
        otherGroupSignals,
        object,
        group,
        activeInterval,
      )
      // Отмечаем чекбоксы датчиков, внесших максимальный вклад в аномалию
      if (topGroupSignals.value.length)
        topCheckbox.value = topGroupSignals.value.map(({ kks }) => kks)
    })

    watch([object, group, intervals, activeInterval], async () => {
      topCheckbox.value = []
      otherCheckbox.value = []
      await getTopAndOtherGroupSignals(
        topGroupSignals,
        otherGroupSignals,
        object,
        group,
        activeInterval,
      )
      // Отмечаем чекбоксы датчиков, внесших максимальный вклад в аномалию
      if (topGroupSignals.value.length)
        topCheckbox.value = topGroupSignals.value.map(({ kks }) => kks)
    })

    // Прослушка процента выполнения построения отчета интервала
    socket.on('setPercentIntervalReport', percents => {
      percentIntervalReport.value = percents
    })

    return {
      currentRoute,
      activeInterval,
      activeIntervalLabel,
      topGroupSignals,
      topCheckbox,
      otherGroupSignals,
      otherCheckbox,
      percentIntervalReport,
      intervalReportActive,
      onIntervalReportButtonClick,
    }
  },
}
</script>

<template>
  <div :style="{ padding: '0px 20px 0px 20px' }">
    <div class="container-fluid">
      <div class="row align-items-center">
        <div
          class="col-md-7 text-begin"
          :style="{ padding: '0px 10px 0px 0px' }"
        >
          <h4>{{ activeIntervalLabel }}</h4>
        </div>
        <div class="col-md-2 text-end">
          <Button
            @click="onIntervalReportButtonClick"
            :disabled="intervalReportActive"
            >PDF отчет</Button
          >
        </div>
        <div
          class="col-md-3"
          v-if="intervalReportActive"
          :style="{ padding: '0px 0px 0px 10px' }"
        >
          <ProgressBar :value="percentIntervalReport"></ProgressBar>
        </div>
      </div>
    </div>
    <UPlotlyInterval
      :headerTitle="'График вероятности наступления аномалии за весь период'"
      :activeInterval="activeInterval"
    ></UPlotlyInterval>
    <div class="container-fluid interval-padding-signals">
      <div class="row" v-if="topGroupSignals.length">
        <div class="col">
          <h3 class="interval-h3-color">Сигналы, внесшие наибольший вклад</h3>
        </div>
      </div>
      <div class="row" v-for="top in topGroupSignals">
        <div class="col">
          <Checkbox
            v-model="topCheckbox"
            :input-id="top.kks"
            name="topCheckobx"
            :value="top.kks"
            :disabled="intervalReportActive"
          ></Checkbox>
          <label :for="top.kks">{{
            top.kks + ' (' + top.description + ')'
          }}</label>
        </div>
      </div>
      <div class="row" v-if="otherGroupSignals.length">
        <div class="col">
          <h3 class="interval-h3-color">Остальные сигналы группы</h3>
        </div>
      </div>
      <div class="row" v-for="other in otherGroupSignals">
        <div class="col">
          <Checkbox
            v-model="otherCheckbox"
            :input-id="other.kks"
            name="otherCheckbox"
            :value="other.kks"
            :disabled="intervalReportActive"
          ></Checkbox>
          <label :for="other.kks">{{
            other.kks + ' (' + other.description + ')'
          }}</label>
        </div>
      </div>
    </div>
    <br />
    <div v-for="top in topGroupSignals" v-if="topGroupSignals.length">
      <div v-if="topCheckbox.includes(top.kks)">
        <UPlotlyMultipleAxes
          :headerTitle="`${top.kks} (${top.description})`"
          :mainSignal="top"
          :idPrefix="'top-' + top.kks + '-'"
          :activeInterval="activeInterval"
          :disabled="intervalReportActive"
          :typeOfMainSignal="'top'"
        ></UPlotlyMultipleAxes>
      </div>
    </div>
    <div v-for="other in otherGroupSignals" v-if="otherGroupSignals.length">
      <div v-if="otherCheckbox.includes(other.kks)">
        <UPlotlyMultipleAxes
          :headerTitle="`${other.kks} (${other.description})`"
          :mainSignal="other"
          :idPrefix="'other-' + other.kks + '-'"
          :activeInterval="activeInterval"
          :disabled="intervalReportActive"
          :typeOfMainSignal="'other'"
        ></UPlotlyMultipleAxes>
      </div>
    </div>
  </div>
</template>

<style>
.interval-padding-signals {
  padding: 0 10px 0 0;
}
.interval-h3-color {
  color: #1f77b4;
}
</style>
