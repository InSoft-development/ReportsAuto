import { defineStore, storeToRefs } from 'pinia'
import { ref, reactive, computed } from 'vue'

export const useApplicationStore = defineStore('ApplicationStore', () => {
  const intervals = ref([])
  const object = ref('')
  const group = ref(0)

  const collapsed = ref(false)
  const sidebarWidthUncollapsed = '400px'
  const sidebarWidthCollapsed = '65px'
  const sidebarWidth = computed(() => {
    return collapsed.value ? sidebarWidthCollapsed : sidebarWidthUncollapsed
  })
  const loadStateSidebar = ref(false)

  const activeSignals = reactive({
    top: {},
    other: {},
  })

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

  return {
    intervals,
    object,
    group,
    collapsed,
    sidebarWidth,
    loadStateSidebar,
    activeSignals,
    setActiveSignals,
  }
})
