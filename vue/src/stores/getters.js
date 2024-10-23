import { storeToRefs } from 'pinia'
import { useApplicationStore } from './applicationStore'
import axios from 'axios'

const URL = window.api.url

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

export async function updatePlotlyInterval(
  data,
  layout,
  objectSelected,
  groupSelected,
  intervalSelected='all'
) {
  let url = URL + 'api/update_plotly_interval/'

  await axios
    .get(url, {
      params: {
        objectSelected: objectSelected.value,
        groupSelected: groupSelected.value,
        intervalSelected: intervalSelected
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
