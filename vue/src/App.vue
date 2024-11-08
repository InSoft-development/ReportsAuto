<script>
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from './stores/applicationStore'

export default {
  setup() {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { intervals, object, group, loadStateSidebar, sidebarWidth } =
      storeToRefs(applicationStore)

    // Переадресация URL
    const router = useRouter()
    // Определение текущего URL
    const route = useRoute()
    const currentRoute = computed(() => route.path)
    // Из URL достаем номер интервала для активизации вкладки табовой панели
    const activeIndexTab = computed(() => {
      return Number(route.params.intervalsId)
    })

    const routeToHome = () => {
      if (currentRoute.value !== '/addition') router.push('/')
    }

    return {
      routeToHome,
      object,
      group,
      intervals,
      loadStateSidebar,
      currentRoute,
      activeIndexTab,
      sidebarWidth,
    }
  },
}
</script>

<template>
  <header>
    <div class="wrapper"></div>
  </header>
  <USidebar @redirectToHome="routeToHome"></USidebar>
  <div
    v-if="currentRoute !== '/settings'"
    :style="{ padding: '0px 20px 0px 20px', 'margin-left': sidebarWidth }"
  >
    <h1 class="text-center">Объект {{ object }}: группа {{ group }}</h1>
    <TabView
      v-if="currentRoute !== '/addition'"
      :scrollable="true"
      :active-index="activeIndexTab"
    >
      <TabPanel
        v-for="interval in intervals"
        :key="interval.title"
        :disabled="loadStateSidebar"
      >
        <template #header>
          <span
            class="p-tabview-title"
            data-pc-section="headertitle"
            :style="{ display: 'block', height: 'inherit' }"
          >
            <RouterLink
              :to="interval.href"
              :style="{ display: 'block', height: 'inherit' }"
              >{{ interval.title }}</RouterLink
            >
          </span>
        </template>
      </TabPanel>
    </TabView>
    <ProgressSpinner
      v-if="loadStateSidebar"
      style="width: 100px; height: 100px"
      stroke-width="5"
      animation-duration=".3s"
      class="z-2 center-screen"
    />
  </div>
  <RouterView :style="{ 'margin-left': sidebarWidth }" />
</template>

<style>
.center-screen {
  position: fixed;
  left: 50%;
  top: 50%;
}
.p-tabview-panels {
  display: none;
}
</style>
