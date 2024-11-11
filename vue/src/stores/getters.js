import { storeToRefs } from 'pinia'
import { useApplicationStore } from './applicationStore'
import axios from 'axios'

const URL = window.api.url

/**
 * Процедура инициализации меню sidebar
 * @param objectSelected ref ссылка выбранного объекта
 * @param objectOptions ref ссылка доступных для выбора объектов
 * @param groupSelected ref ссылка выбранной группы
 * @param groupOptions ref ссылка доступных для выбора групп
 * @param sidebarMenu ref ссылка на объект sidebar
 * @returns {Promise<void>}
 */
export async function initSidebar(
  objectSelected,
  objectOptions,
  groupSelected,
  groupOptions,
  sidebarMenu,
) {
  let url = URL + 'api/init_sidebar/'
  let childIntervals = []
  await axios
    .get(url)
    .then(res => {
      objectSelected.value = res.data.object
      objectOptions.value = res.data.objects
      groupSelected.value = res.data.group
      groupOptions.value = res.data.groups

      for (const [index, interval] of res.data.intervals.entries()) {
        childIntervals.push({
          href: `/interval/${index}`,
          title: `${interval[0]} -- ${interval[1]}`,
          hiddenOnCollapse: true,
        })
      }

      sidebarMenu.value = [
        {
          header: 'Меню',
          hiddenOnCollapse: true,
        },
        {
          href: '/',
          title: 'Интервалы',
          icon: 'bi bi-menu-down',
          child: childIntervals,
        },
        {
          href: '/addition',
          title: 'Дополнения',
          icon: 'bi bi-bar-chart',
        },
        {
          href: '/settings',
          title: 'Настройки',
          icon: 'bi bi-gear',
        },
      ]

      // Заносим в хранилище pinia изменения
      const applicationStore = useApplicationStore()
      const { intervals, object, group } = storeToRefs(applicationStore)
      object.value = objectSelected.value
      group.value = groupSelected.value
      intervals.value = childIntervals
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процедура обновления меню sidebar
 * @param objectSelected ref ссылка выбранного объекта
 * @param groupSelected ref ссылка выбранной группы
 * @param groupOptions ref ссылка доступных для выбора групп
 * @param sidebarChildInterval ref ссылка на объект интервалов в объекте sidebar
 * @param cause причина обновления (переключение объекта станции | переключение группы )
 * @returns {Promise<void>}
 */
export async function updateSidebar(
  objectSelected,
  groupSelected,
  groupOptions,
  sidebarChildInterval,
  cause,
) {
  let url = URL + 'api/update_sidebar/'
  let childIntervals = []
  sidebarChildInterval.child = [{}]

  await axios
    .get(url, {
      params: {
        objectSelected: objectSelected.value,
        groupSelected: groupSelected.value,
        cause: cause,
      },
    })
    .then(res => {
      groupSelected.value = res.data.group
      groupOptions.value = res.data.groups
      for (const [index, interval] of res.data.intervals.entries()) {
        childIntervals.push({
          href: `/interval/${index}`,
          title: `${interval[0]} -- ${interval[1]}`,
          hiddenOnCollapse: true,
        })
      }
      sidebarChildInterval.child = childIntervals

      // Заносим в хранилище pinia изменения
      const applicationStore = useApplicationStore()
      const { intervals, object, group } = storeToRefs(applicationStore)
      object.value = objectSelected.value
      group.value = groupSelected.value
      intervals.value = childIntervals
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процедура инициализации параметров постобработки
 * @param postProcessing ref ссылка на объект постобработки
 * @returns {Promise<void>}
 */
export async function initPostProcessing(postProcessing) {
  let url = URL + 'api/init_post_processing/'
  await axios
    .get(url)
    .then(res => {
      postProcessing.value = res.data.postProcessing
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процедура обновления данных графика вероятности на всем периоде или интервале
 * @param data ref ссылка на объект data графика
 * @param layout ref ссылка на объект layout графика
 * @param objectSelected ref ссылка выбранного объекта
 * @param groupSelected ref ссылка выбранной группы
 * @param intervalSelected выбранный интервал (номер | 'all' - весь фрейм по умолчанию)
 * @returns {Promise<void>}
 */
export async function updatePlotlyInterval(
  data,
  layout,
  objectSelected,
  groupSelected,
  intervalSelected = 'all',
) {
  let url = URL + 'api/update_plotly_interval/'

  await axios
    .get(url, {
      params: {
        objectSelected: objectSelected.value,
        groupSelected: groupSelected.value,
        intervalSelected: intervalSelected,
      },
    })
    .then(res => {
      data.value = res.data.data
      layout.value = res.data.layout
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процедура получения топовых и остальных датчиков группы
 * @param topGroupSignals ref ссылка топовых датчиков
 * @param otherGroupSignals ref ссылка остальных датчиков группы
 * @param objectSelected ref ссылка выбранного объекта
 * @param groupSelected ref ссылка выбранной группы
 * @param intervalSelected ref ссылка выбранного интервала
 * @returns {Promise<void>}
 */
export async function getTopAndOtherGroupSignals(
  topGroupSignals,
  otherGroupSignals,
  objectSelected,
  groupSelected,
  intervalSelected,
) {
  let url = URL + 'api/get_signals/'

  await axios
    .get(url, {
      params: {
        objectSelected: objectSelected.value,
        groupSelected: groupSelected.value,
        intervalSelected: intervalSelected.value,
      },
    })
    .then(res => {
      topGroupSignals.value = res.data.top
      otherGroupSignals.value = res.data.other
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процудра получения дополнительных сигналов многоосевого графика
 * @param signals ref ссылка на массив объектов сигналов
 * @param mainSignalRef ref ссылка основного сигнала
 * @param objectSelected ref ссылка выбранного объекта
 * @returns {Promise<void>}
 */
export async function getAdditionalsSignals(
  signals,
  mainSignalRef,
  objectSelected,
) {
  let url = URL + 'api/get_additional_signals/'

  await axios
    .get(url, {
      params: {
        mainSignal: mainSignalRef.value.kks,
        objectSelected: objectSelected.value,
      },
    })
    .then(res => {
      signals.value = res.data.additionalSignals
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процедура обновления данных многоосевого графика
 * @param data ref ссылка на объект data графика
 * @param layout ref ссылка на объект layout графика
 * @param mainSignalRef ref ссылка основного сигнала
 * @param objectSelected ref ссылка выбранного объекта
 * @param intervalSelected ref ссылка выбранного интервала
 * @param signals ref ссылка на массив объектов сигналов
 * @param signalsCheckbox  ref ссылка на массив выбранных чекбоксов сигналов многоосевого графика
 * @returns {Promise<void>}
 */
export async function updatePlotlyMultipleAxes(
  data,
  layout,
  mainSignalRef,
  objectSelected,
  intervalSelected,
  signals,
  signalsCheckbox,
) {
  let url = URL + 'api/update_plotly_multiple_axes/'

  await axios
    .get(url, {
      params: {
        mainSignal: mainSignalRef.value.kks,
        objectSelected: objectSelected.value,
        intervalSelected: intervalSelected,
        signals: signals.value.map(({ kks }) => kks),
        activeCheckbox: signalsCheckbox.value,
      },
    })
    .then(res => {
      data.value = res.data.data
      layout.value = res.data.layout
    })
    .catch(error => {
      console.log(error)
    })
}

/**
 * Процедра обновления данных гистограммы распределения
 * @param data ref ссылка на объект data гистограммы
 * @param layout ref ссылка на объект layout гистограммы
 * @returns {Promise<void>}
 */
export async function updatePlotlyHistogram(data, layout) {
  let url = URL + 'api/update_plotly_histogram/'

  await axios
    .get(url)
    .then(res => {
      data.value = res.data.data
      layout.value = res.data.layout
    })
    .catch(error => {
      console.log(error)
    })
}
