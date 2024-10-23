import axios from 'axios'
import { socket } from '../socket'

const URL = window.api.url


export async function startIntervalDetection(postProcessing) {
  // let url = URL + 'api/interval_detection/'
  await new Promise((resolve) => {
    socket.emit('/api/interval_detection/', postProcessing.value, (res) => {
      if ('causeException' in res) {
        if (res.status === "success") {
          console.log(res.causeException)
          resolve(res)
          return
        }
        if (res.status === "error") {
          console.error(res.causeException)
          alert(res.causeException + "\nВосстановлен предыдущий конфиг и фреймы")
          resolve(res)
          return
        }
      }
      if (res.status === "success") console.log("Интервалы выделены")
      resolve(res)
    })
  })
  // await axios
  //   .post(url, postProcessing.value, {
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //   })
  //   .then(res => {
  //     if ('causeException' in res.data) {
  //       if (res.data.status === "success") {
  //         console.log(res.data.causeException)
  //         return
  //       }
  //       if (res.data.status === "error") {
  //         console.error(res.data.causeException)
  //         alert(res.data.causeException + "\nВосстановлен предыдущий конфиг и фреймы")
  //         return
  //       }
  //     }
  //     if (res.data.status === "success") console.log("Интервалы выделены")
  //   })
  //   .catch(error => {
  //     console.log(error)
  //   })
}

export async function cancelIntervalDetection() {
  // let url = URL + 'api/cancel_interval_detection/'
  await new Promise((resolve) => {
    socket.emit('/api/cancel_interval_detection/', (res) => {
      if (res.status === "success") console.log("Отмена выделения интервалов")
      if (res.status === "error") console.log("Доступ запрещен")
      resolve(res)
    })
  })
  // await axios
  //   .post(url)
  //   .then(res => {
  //     if (res.data.status === "success") console.log("Отмена выделения инетрвалов")
  //   })
  //   .catch(error => {
  //     console.log(error)
  //   })
}
