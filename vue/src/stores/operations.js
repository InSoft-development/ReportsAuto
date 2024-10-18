import axios from 'axios'

const URL = window.api.url

export async function startIntervalDetection(postProcessing) {
  let url = URL + 'api/interval_detection/'
  await axios
    .post(url, postProcessing.value, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(res => {
      console.log(res.data.test)
    })
    .catch(error => {
      console.log(error)
    })
}
