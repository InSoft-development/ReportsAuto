import USidebar from './USidebar.vue'
import UDialog from './UDialog.vue'
import UPlotlyInterval from './UPlotlyInterval.vue'
import UPlotlyMultipleAxes from './UPlotlyMultipleAxes.vue'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap'

import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import FloatLabel from 'primevue/floatlabel'
import ConfirmDialog from 'primevue/confirmdialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import ProgressSpinner from 'primevue/progressspinner'
import ProgressBar from 'primevue/progressbar'
import Checkbox from 'primevue/checkbox'

import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css'

const components = [
  {
    name: 'USidebar',
    component: USidebar,
  },
  {
    name: 'UDialog',
    component: UDialog,
  },
  {
    name: 'UPlotlyInterval',
    component: UPlotlyInterval,
  },
  {
    name: 'UPlotlyMultipleAxes',
    component: UPlotlyMultipleAxes,
  },
  {
    name: 'Button',
    component: Button,
  },
  {
    name: 'Dialog',
    component: Dialog,
  },
  {
    name: 'InputNumber',
    component: InputNumber,
  },
  {
    name: 'FloatLabel',
    component: FloatLabel,
  },
  {
    name: 'ConfirmDialog',
    component: ConfirmDialog,
  },
  {
    name: 'TabView',
    component: TabView,
  },
  {
    name: 'TabPanel',
    component: TabPanel,
  },
  {
    name: 'ProgressSpinner',
    component: ProgressSpinner,
  },
  {
    name: 'ProgressBar',
    component: ProgressBar,
  },
  {
    name: 'Checkbox',
    component: Checkbox,
  },
]

export default {
  install(app) {
    components.forEach(({ name, component }) => {
      app.component(name, component)
    })
  },
}
