import { defineStore, storeToRefs } from 'pinia'
import { ref, reactive, computed } from 'vue'

export const useApplicationStore = defineStore('ApplicationStore', () => {
  const intervals = ref([]) // интервалы в виде массива строк
  const object = ref('') // текущий выбранный объект
  const group = ref(0) // текущая выбранная группа

  const collapsed = ref(false) // статус открытия/закрытия sidebar
  const sidebarWidthUncollapsed = '400px' // длина sidebar в открытом состоянии
  const sidebarWidthCollapsed = '65px' // длина sidebar в закрытом состоянии
  // вычислимое свойство длины sidebar от его состояния
  const sidebarWidth = computed(() => {
    return collapsed.value ? sidebarWidthCollapsed : sidebarWidthUncollapsed
  })
  const loadStateSidebar = ref(false) // состояние выполнение операций и флаг блокировки компонентов меню

  // reactive объект активных топовых и остальных датчиков с выбранными чекбоксами сигналов для составления отчета на интервале
  const activeSignals = reactive({
    top: {},
    other: {},
  })

  // функция занесения выбранного топового или другого датчика в activeSignals
  const setActiveSignals = (
    typeSignal,
    mainSignal,
    signals,
    signalsCheckbox,
  ) => {
    activeSignals[typeSignal][mainSignal] = {
      signals: signals,
      activeSignals: signalsCheckbox,
    }
  }

  const commonReportSettings = reactive({
    formatRadio: 'A3',
    landscape: false
  })

  const intervalReportSettings = reactive({
    formatRadio: 'A3',
    landscape: false
  })

  return {
    intervals,
    object,
    group,
    collapsed,
    sidebarWidth,
    loadStateSidebar,
    activeSignals,
    setActiveSignals,
    commonReportSettings,
    intervalReportSettings
  }
})
