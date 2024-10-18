<script>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { SidebarMenu } from 'vue-sidebar-menu'

import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

import { useApplicationStore } from '../../stores/applicationStore'

import { initSidebar, updateSidebar } from '../../stores'

export default {
  name: 'USidebar',
  components: {
    SidebarMenu,
  },
  emits: ['redirectToHome', 'changeSidebarWidth'],
  setup(props, context) {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { loadStateSidebar } = storeToRefs(applicationStore)
    // Меню sidebar
    const sidebarMenu = ref([])

    // Определение сокрытия меню sidebar
    const collapsed = ref(false)

    // Определение ширины меню sidebar
    const sidebarWidthUncollapsed = '400px'
    const sidebarWidthCollapsed = '65px'
    const sidebarWidth = computed(() => {
      context.emit(
        'changeSidebarWidth',
        collapsed.value ? sidebarWidthCollapsed : sidebarWidthUncollapsed,
      )
      return collapsed.value ? sidebarWidthCollapsed : sidebarWidthUncollapsed
    })

    // Select объектов станций
    const objectSelected = ref('')
    const objectOptions = ref([])

    // Select группы
    const groupSelected = ref('')
    const groupOptions = ref([])

    // Обработчик изменения селекта объекта или группы в sidebar
    const changeObjectGroup = async byCause => {
      loadStateSidebar.value = true
      await updateSidebar(
        objectSelected,
        groupSelected,
        groupOptions,
        sidebarMenu.value[1],
        byCause,
      )
      context.emit('redirectToHome')
      loadStateSidebar.value = false
    }

    // Флаг показа диалогового окна выделения интервалов
    const dialogActive = ref(false)

    const onDialogButtonClick = () => {
      dialogActive.value = !dialogActive.value
    }

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      loadStateSidebar.value = true
      // Инициализируем sidebar начальными значениями
      await initSidebar(
        objectSelected,
        objectOptions,
        groupSelected,
        groupOptions,
        sidebarMenu,
      )
      loadStateSidebar.value = false
    })

    return {
      loadStateSidebar,
      sidebarMenu,
      collapsed,
      sidebarWidth,
      objectSelected,
      objectOptions,
      groupSelected,
      groupOptions,
      changeObjectGroup,
      dialogActive,
      onDialogButtonClick,
    }
  },
}
</script>

<template>
  <sidebar-menu
    class="sidebar-color"
    :menu="sidebarMenu"
    v-model:collapsed="collapsed"
    :disableHover="true"
    :width="sidebarWidth"
    :widthCollapsed="sidebarWidth"
  >
    <template v-slot:footer v-if="!collapsed">
      <div class="sidebar-select">
        <select
          v-model="objectSelected"
          class="sidebar-select-object"
          aria-label="Селект выборки объекта"
          id="select-object"
          :disabled="loadStateSidebar"
          @change="changeObjectGroup('object')"
        >
          <option v-for="option in objectOptions" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div class="sidebar-select">
        <select
          v-model="groupSelected"
          class="sidebar-select-group"
          aria-label="Селект выбора группы"
          id="select-group"
          :disabled="loadStateSidebar"
          @change="changeObjectGroup('group')"
        >
          <option v-for="(option, index) in groupOptions" :value="index">
            {{ index }}
          </option>
        </select>
      </div>
      <div class="sidebar-div-button">
        <div class="sidebar-button-wrapper">
          <Button class="sidebar-button" :disabled="loadStateSidebar"
            >PDF</Button
          >
        </div>
        <!--      <div v-if="progressBarActive">-->
        <!--        <ProgressBar class="col-10 align-self-center" :value="progressBarValue"></ProgressBar>-->
        <!--      </div>-->
      </div>
      <div class="sidebar-div-button">
        <div class="sidebar-button-wrapper">
          <Button
            class="sidebar-button"
            @click="onDialogButtonClick"
            :disabled="loadStateSidebar"
            >Выделение интервалов</Button
          >
          <UDialog
            :visible="dialogActive"
            @closeDialog="onDialogButtonClick"
          ></UDialog>
        </div>
      </div>
    </template>
  </sidebar-menu>
</template>

<style scoped>
.sidebar-color {
  background-color: #1e293b;
  color: #fff;
}
.sidebar-select {
  background: #1e293b;
  border-radius: 5px;
  color: #fff;
  min-width: 150px;
  display: block;
  cursor: pointer;
  padding: 10px 20px 10px 1.2em;
  margin-bottom: 5px;
}
.sidebar-select-object {
  color: #fff;
  background: #1e293b;
  border-radius: 5px;
  min-width: 150px;
  display: block;
  cursor: pointer;
  padding: 10px 10px 10px 1.2em;
  margin-bottom: 5px;
}
.sidebar-select-group {
  color: #fff;
  background: #1e293b;
  border-radius: 5px;
  min-width: 150px;
  display: block;
  cursor: pointer;
  padding: 10px 10px 10px 1.2em;
  margin-bottom: 5px;
}
.sidebar-div-button {
  display: inline-block;
  margin-bottom: 5px;
  padding: 0 0 0 20px;
  font-size: 14px;
  font-weight: 400;
  text-transform: uppercase;
  text-decoration: none;
}
.sidebar-button-wrapper {
  margin-bottom: 5px;
}
.sidebar-button {
  display: inline-block;
  margin-bottom: 5px;
  background: #1e293b;
  border: 1px solid #fff;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 400;
  color: #fff;
  text-transform: uppercase;
  text-decoration: none;
  transition:
    background 0.1s linear,
    color 0.1s linear;
}
.sidebar-button:hover {
  background-color: #fff;
  color: #1e293b;
}
</style>
