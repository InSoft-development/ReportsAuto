<script>
import { ref, onMounted, toRef, onUnmounted, onBeforeUnmount } from 'vue'
import { useConfirm } from 'primevue/useconfirm'

import {
  initPostProcessing,
  startIntervalDetection,
  cancelIntervalDetection,
} from '../../stores'

import { socket } from '../../socket'

export default {
  name: 'UDialog',
  props: {
    visible: Boolean,
  },
  emits: ['closeDialog', 'redirect'],
  setup(props, context) {
    // Ссылка видимости диалога на проп для сохранениея реактивности
    const visibleRef = toRef(props, 'visible')
    const closeDialog = async () => {
      // Если уже начали процесс выделения интервалов
      if (dialogElementsDisable.value) {
        await cancelIntervalDetection()
        return
      }
      context.emit('closeDialog')
      // Восстанавливаем значения постобработки, если не стали выделять интервалы
      await initPostProcessing(postProcessing)
    }

    const redirectAfterIntervalDetection = async () => {
      context.emit('redirect')
      // Восстанавливаем значения постобработки, если не стали выделять интервалы
      await initPostProcessing(postProcessing)
    }

    // Отключение элементов диалогового окна
    const dialogElementsDisable = ref(false)

    // Параметры пост обработки
    const postProcessing = ref({
      rollInHours: Number(),
      countContinueLong: Number(),
      countContinueShort: Number(),
      countTop: Number(),
      lenLong: Number(),
      lenShort: Number(),
      thresholdLong: Number(),
      thresholdShort: Number(),
    })

    // Процент выделения интервалов
    const percentIntervalDetection = ref(0)

    // Диалоговое окно подтверждения выделения интервалов
    const confirm = useConfirm()
    const confirmStartInterval = () => {
      confirm.require({
        message: 'Вы действительго хотите запустить выделение интервалов?',
        header: 'Подтверждение начала выделения интервалов',
        icon: 'pi pi-exclamation-triangle',
        rejectClass: 'p-button-secondary p-button-outlined',
        rejectLabel: 'Отмена',
        acceptLabel: 'Подтвердить',
        accept: () => {
          startInterval()
        },
        reject: () => {
          return
        },
      })
    }

    // Запуск выделения интервалов
    const startInterval = async () => {
      percentIntervalDetection.value = 0
      dialogElementsDisable.value = true
      await startIntervalDetection(postProcessing)
      // Инициализируем диалоговое окно постобработки сохраненными значениями
      // await initPostProcessing(postProcessing)
      await redirectAfterIntervalDetection()
      dialogElementsDisable.value = false
    }

    // Хук, вызываемый после монтажа компонента для его инициализации
    onMounted(async () => {
      // Регистрируем событие закрытия веб-приложения
      window.addEventListener('beforeunload', async event => {
        await cancelIntervalDetection()
      })
      dialogElementsDisable.value = true
      // Инициализируем диалоговое окно постобработки начальными значениями
      await initPostProcessing(postProcessing)
      dialogElementsDisable.value = false
    })

    // Хук, вывываемый перед размонтировкой компонента - закрытие веб-приложения
    onBeforeUnmount(async () => {
      window.removeEventListener('beforeunload', async event => {})
    })

    // Хук, вызываемый при размонтировки компонента - закрытие веб-приложения
    onUnmounted(async () => {
      await cancelIntervalDetection()
    })

    // Прослушка процента выполнения выделения интервалов
    socket.on('setPercentIntervalDetection', percents => {
      percentIntervalDetection.value = percents
    })

    return {
      visibleRef,
      closeDialog,
      dialogElementsDisable,
      postProcessing,
      percentIntervalDetection,
      confirmStartInterval,
    }
  },
}
</script>

<template>
  <Dialog
    class="sidebar-dialog"
    :visible="visibleRef"
    :closable="false"
    modal
    draggable
    header="Выделение интервалов"
    position="left"
    :style="{ width: '50rem' }"
  >
    <div class="container">
      <div class="row sidebar-dialog-row">
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.rollInHours"
              id="post-processing-roll_in_hours"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-roll_in_hours"
              >Сглаживание в часах</label
            >
          </FloatLabel>
        </div>
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.countTop"
              id="post-processing-count-top"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="1"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-count-top"
              >Датчики, внесшие максимальный вклад</label
            >
          </FloatLabel>
        </div>
      </div>
      <div class="row sidebar-dialog-row">
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.thresholdShort"
              id="post-processing-threshold_short"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :max="100"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-threshold_short">Threshold short</label>
          </FloatLabel>
        </div>
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.thresholdLong"
              id="post-processing-threshold_long"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :max="100"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-threshold_long">Threshold long</label>
          </FloatLabel>
        </div>
      </div>
      <div class="row sidebar-dialog-row">
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.lenShort"
              id="post-processing-len_short"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-len_short">Len short</label>
          </FloatLabel>
        </div>
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.lenLong"
              id="post-processing-len_long"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-len_long">Len long</label>
          </FloatLabel>
        </div>
      </div>
      <div class="row sidebar-dialog-row">
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.countContinueShort"
              id="post-processing-count_continue_short"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-count_continue_short"
              >Count continue short</label
            >
          </FloatLabel>
        </div>
        <div class="col">
          <FloatLabel class="sidebar-dialog-input_number_float_label">
            <InputNumber
              v-model:modelValue="postProcessing.countContinueLong"
              id="post-processing-count_continue_long"
              :showButtons="true"
              mode="decimal"
              :useGrouping="false"
              :min="0"
              :step="1"
              :allowEmpty="false"
              :disabled="dialogElementsDisable"
            />
            <label for="post-processing-count_continue_long"
              >Count continue long</label
            >
          </FloatLabel>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="container">
        <div class="row align-items-center">
          <div class="col-4">
            <ProgressBar
              v-if="dialogElementsDisable"
              :value="percentIntervalDetection"
            ></ProgressBar>
          </div>
          <div class="col-2 text-end">
            <Button
              label="Отмена"
              icon="pi pi-times"
              text
              @click="closeDialog"
            />
          </div>
          <div class="col-6 text-end">
            <Button
              label="Запустить выделение интервалов"
              icon="pi pi-check"
              @click="confirmStartInterval"
              :disabled="dialogElementsDisable"
            />
          </div>
        </div>
      </div>
      <ConfirmDialog></ConfirmDialog>
    </template>
  </Dialog>
</template>

<style>
.sidebar-dialog {
  background-color: #1e293b;
}
.sidebar-dialog-input_number_float_label {
  font-size: 20px;
  font-weight: bold;
  margin: 10px 0 0 0;
  padding-left: 10px;
}
.sidebar-dialog-row {
  margin: 30px 0 20px 0;
}
</style>
