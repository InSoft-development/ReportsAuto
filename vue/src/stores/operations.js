import axios from 'axios'
import { socket } from '../socket'

const URL = window.api.url

export async function startIntervalDetection(postProcessing) {
  await new Promise(resolve => {
    socket.emit('/api/interval_detection/', postProcessing.value, res => {
      if ('causeException' in res) {
        if (res.status === 'success') {
          console.log(res.causeException)
          resolve(res)
          return
        }
        if (res.status === 'error') {
          console.error(res.causeException)
          alert(
            res.causeException + '\nВосстановлен предыдущий конфиг и фреймы',
          )
          resolve(res)
          return
        }
      }
      if (res.status === 'success') console.log('Интервалы выделены')
      resolve(res)
    })
  })
}

export async function cancelIntervalDetection() {
  await new Promise(resolve => {
    socket.emit('/api/cancel_interval_detection/', res => {
      if (res.status === 'success') console.log('Отмена выделения интервалов')
      if (res.status === 'error') console.log('Доступ запрещен')
      resolve(res)
    })
  })
}

export async function startCommonReport(objectSelected, groupSelected) {
  await new Promise(resolve => {
    socket.emit('/api/common_report/', objectSelected.value, groupSelected.value, res => {
      if ('error' in res) {
        alert(res.error)
        return 'error'
      }
      resolve(res)
    })
  })
}

export async function startIntervalReport(objectSelected,
                                          groupSelected,
                                          intervalSelected,
                                          topGroupSignals,
                                          otherGroupSignals,
                                          activeSignals) {

  await new Promise(resolve => {
    socket.emit('/api/interval_report/',
        objectSelected.value,
        groupSelected.value,
        intervalSelected.value,
        topGroupSignals.value.map(({ kks }) => kks),
        otherGroupSignals.value.map(({ kks }) => kks),
        activeSignals,
            res => {
      if ('error' in res) {
        alert(res.error)
        return 'error'
      }
      resolve(res)
    })
  })
}
