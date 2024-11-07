<script>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { SidebarMenu } from 'vue-sidebar-menu'

import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

import { useApplicationStore } from '../../stores/applicationStore'

import { initSidebar, updateSidebar, startCommonReport } from '../../stores'

import { socket } from '../../socket'
import axios from 'axios'
import jsPDF from 'jspdf'

export default {
  name: 'USidebar',
  components: {
    SidebarMenu,
  },
  emits: ['redirectToHome'],
  setup(props, context) {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { loadStateSidebar, collapsed, sidebarWidth } =
      storeToRefs(applicationStore)
    // Меню sidebar
    const sidebarMenu = ref([])

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

    const onRedirectAfterIntervalDetection = async () => {
      loadStateSidebar.value = true
      dialogActive.value = !dialogActive.value
      await updateSidebar(
        objectSelected,
        groupSelected,
        groupOptions,
        sidebarMenu.value[1],
        'object',
      )
      context.emit('redirectToHome')
      loadStateSidebar.value = false
    }

    // Процент построения отчета по всем периодам
    const percentCommonReport = ref(0)
    // Флаг показа ProgressBar
    const commonReportActive = ref(false)

    const onCommonReportButtonClick = async () => {
      percentCommonReport.value = 0
      loadStateSidebar.value = true
      commonReportActive.value = true
      let status = await startCommonReport(objectSelected, groupSelected)
      if (status !== 'error') {
        const URL = window.api.url
        // Загрузка файла html
        const linkCommonReportHtml = document.createElement('a')
        linkCommonReportHtml.download = `common_report_${objectSelected.value}_group_${groupSelected.value}.html`

        await axios
          .get(URL + '/common_report.html', {
            params: { objectSelected: objectSelected.value },
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
        linkCommonReportPdf.download = `common_report_${objectSelected.value}_group_${groupSelected.value}.pdf`

        await axios
          .get(URL + '/common_report.pdf', {
            params: { objectSelected: objectSelected.value },
            responseType: 'blob',
          })
          .then(res => {
            linkCommonReportPdf.href = window.URL.createObjectURL(
              new Blob([res.data], { type: 'application/pdf' }),
            )
            linkCommonReportPdf.click()
            linkCommonReportPdf.remove()
            window.URL.revokeObjectURL(linkCommonReportPdf.href)
          })
          .catch(error => {
            console.log(error)
          })
      }
      percentCommonReport.value = 100
      commonReportActive.value = false

      loadStateSidebar.value = false
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

    // Прослушка процента выполнения построения отчета
    socket.on('setPercentCommonReport', percents => {
      percentCommonReport.value = percents
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
      onRedirectAfterIntervalDetection,
      percentCommonReport,
      commonReportActive,
      onCommonReportButtonClick,
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
          <Button
            class="sidebar-button"
            @click="onCommonReportButtonClick"
            :disabled="loadStateSidebar"
            >PDF</Button
          >
        </div>
        <div v-if="commonReportActive">
          <ProgressBar
            class="col-10 align-self-center"
            :value="percentCommonReport"
          ></ProgressBar>
        </div>
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
            @redirect="onRedirectAfterIntervalDetection"
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
