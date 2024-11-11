import axios from 'axios'
import { socket } from '../socket'

const URL = window.api.url

/**
 * Процедура запуска выделения интервалов
 * @param postProcessing ref ссылка на объект постобработки
 * @returns {Promise<void>}
 */
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

/**
 * Процедура отмены выделения интервалов
 * @returns {Promise<void>}
 */
export async function cancelIntervalDetection() {
  await new Promise(resolve => {
    socket.emit('/api/cancel_interval_detection/', res => {
      if (res.status === 'success') console.log('Отмена выделения интервалов')
      if (res.status === 'error') console.log('Доступ запрещен')
      resolve(res)
    })
  })
}

/**
 * Функция построения общего отчета по группе
 * @param objectSelected ref ссылка выбранного объекта
 * @param groupSelected ref ссылка выбранной группы
 * @param commonReportSettings объект параметров рендера pdf отчета по группе
 * @returns {Promise<string>} статус операции рендеринга
 */
export async function startCommonReport(
  objectSelected,
  groupSelected,
  commonReportSettings,
) {
  let status = ''
  await new Promise(resolve => {
    socket.emit(
      '/api/common_report/',
      objectSelected.value,
      groupSelected.value,
      commonReportSettings,
      res => {
        resolve(res)
        if ('error' in res) {
          alert(res.error)
          status = 'error'
        }
      },
    )
  })
  return status
}

/**
 * Функция построения отчета по интервалу
 * @param objectSelected ref ссылка выбранного объекта
 * @param groupSelected ref ссылка выбранной группы
 * @param intervalReportSettings объект параметров рендера pdf отчета интервала
 * @param intervalSelected ref ссылка выбранного интервала
 * @param topGroupSignals ref ссылка на массив объектов топовых датчиков
 * @param otherGroupSignals ref ссылка на массив объектов остальных датчиков группы
 * @param activeSignals объект активных датчиков и выбранных для отображения на многоосевых графиков сигналов
 * @returns {Promise<string>} статус операции рендеринга
 */
export async function startIntervalReport(
  objectSelected,
  groupSelected,
  intervalReportSettings,
  intervalSelected,
  topGroupSignals,
  otherGroupSignals,
  activeSignals,
) {
  let status = ''
  await new Promise(resolve => {
    socket.emit(
      '/api/interval_report/',
      objectSelected.value,
      groupSelected.value,
      intervalReportSettings,
      intervalSelected.value,
      topGroupSignals.value.map(({ kks }) => kks),
      otherGroupSignals.value.map(({ kks }) => kks),
      activeSignals,
      res => {
        resolve(res)
        if ('error' in res) {
          alert(res.error)
          status = 'error'
        }
      },
    )
  })
  return status
}
