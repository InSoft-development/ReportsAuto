import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import PrimeVue, { defaultOptions } from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'

import globalComponents from './components/global'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(globalComponents)
app.use(PrimeVue)
app.use(ConfirmationService)

app.mount('#app')
