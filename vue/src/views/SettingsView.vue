<script>
import { useApplicationStore } from '../stores/applicationStore'

export default {
  setup() {
    // Инициализация хранилища pinia
    const applicationStore = useApplicationStore()
    const { commonReportSettings, intervalReportSettings } = applicationStore

    return {
      commonReportSettings,
      intervalReportSettings,
    }
  },
}
</script>

<template>
  <div :style="{ padding: '0px 20px 0px 20px' }">
    <div class="container-fluid">
      <div class="row">
        <div class="col">
          <h1 class="text-center">Настройки</h1>
        </div>
      </div>
      <table class="table align-middle table-borderless settings-table">
        <thead class="border-primary">
          <th></th>
          <th>Формат отчета</th>
          <th>Ориентация страниц отчета</th>
        </thead>
        <tbody>
          <tr class="border-bottom border-top border-primary settings-table-tr">
            <th>Общий отчет по группе:</th>
            <td>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="common-A1"
                      value="A1"
                      v-model="commonReportSettings.formatRadio"
                    />
                    <label for="common-A1">A1</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="common-A2"
                      value="A2"
                      v-model="commonReportSettings.formatRadio"
                    />
                    <label for="common-A2">A2</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="common-A3"
                      value="A3"
                      v-model="commonReportSettings.formatRadio"
                    />
                    <label for="common-A3">A3</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="common-A4"
                      value="A4"
                      v-model="commonReportSettings.formatRadio"
                    />
                    <label for="common-A4">A4</label>
                  </div>
                </div>
              </div>
            </td>
            <td>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="common-vertical"
                      :value="false"
                      v-model="commonReportSettings.landscape"
                    />
                    <label for="common-vertical">Вертикальная</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="common-landscape"
                      :value="true"
                      v-model="commonReportSettings.landscape"
                    />
                    <label for="common-landscape">Альбомная</label>
                  </div>
                </div>
              </div>
            </td>
          </tr>
          <tr class="border-primary">
            <th>Отчет по интервалу:</th>
            <td>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="interval-A1"
                      value="A1"
                      v-model="intervalReportSettings.formatRadio"
                    />
                    <label for="interval-A1">A1</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="interval-A2"
                      value="A2"
                      v-model="intervalReportSettings.formatRadio"
                    />
                    <label for="interval-A2">A2</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="interval-A3"
                      value="A3"
                      v-model="intervalReportSettings.formatRadio"
                    />
                    <label for="interval-A3">A3</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="interval-A4"
                      value="A4"
                      v-model="intervalReportSettings.formatRadio"
                    />
                    <label for="interval-A4">A4</label>
                  </div>
                </div>
              </div>
            </td>
            <td>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="interval-vertical"
                      :value="false"
                      v-model="intervalReportSettings.landscape"
                    />
                    <label for="interval-vertical">Вертикальная</label>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="setting-table-radio-button">
                    <input
                      type="radio"
                      id="interval-landscape"
                      :value="true"
                      v-model="intervalReportSettings.landscape"
                    />
                    <label for="interval-landscape">Альбомная</label>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style>
.settings-table {
  --bs-table-bg: transparent;
  border-style: dashed;
  border-color: #0242b6;
  border-width: 5px;
}
.border-primary {
  border-color: #0242b6 !important;
  border-width: 2px;
}
.setting-table-radio-button {
  margin-top: 1px;
  padding-left: 0;
  margin-bottom: 1px;
}
.setting-table-radio-button input {
  cursor: pointer;
}
.setting-table-radio-button label {
  padding: 10px 10px 10px 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  white-space: nowrap;
  position: relative;
}
</style>
