import { defineStore, storeToRefs } from 'pinia'
import { ref, reactive } from 'vue'

export const useApplicationStore = defineStore('ApplicationStore', () => {
  const intervals = ref([])
  const object = ref('')
  const group = ref(0)

  const loadStateSidebar = ref(false)

  return {
    intervals,
    object,
    group,
    loadStateSidebar,
  }
})
