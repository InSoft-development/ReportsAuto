<script>
import { ref, reactive, computed, onMounted, toRef, toRefs, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  setup() {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    // Оборачиваем объеты хранилище в реактивные ссылки
    const { object, group } = storeToRefs(applicationStore)
    return {
      object,
      group,
    }
  },
}
</script>

<template>
  <div :style="{ padding: `0px 20px 0px 20px` }">
    <UPlotlyHistogram
      v-if="group !== 0"
      :headerTitle="'Гистограмма распределения функции потерь датчиков (loss) и вероятности возникновения аномалии (predict)'"
    ></UPlotlyHistogram>
    <div v-else>
      <svg style="display: none">
        <symbol
          id="exclamation-triangle-fill"
          fill="currentColor"
          viewBox="0 0 16 16"
        >
          <path
            d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
          />
        </symbol>
      </svg>
      <div class="alert alert-warning d-flex align-items-center" role="alert">
        <svg
          class="bi flex-shrink-0 me-2"
          width="24"
          height="24"
          role="img"
          aria-label="Warning:"
        >
          <use xlink:href="#exclamation-triangle-fill" />
        </svg>
        <div class="additional-histogram-warning">
          <b>Внимание</b>: Для <u><b>нулевой группы</b></u> гистограмма
          распределения функции потерь датчиков и вероятности не строится
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.additional-histogram-warning {
  text-align: center;
  font-size: 14px;
}
</style>
