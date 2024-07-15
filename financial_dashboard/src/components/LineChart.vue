<template>
  <div class="container">
    <div class="option">
      <el-button
        @click="export_data"
        style="width: 240px"
        size="large"
        type="warning"
        >导出{{ SECUCODE }}的全部数据</el-button
      >

      <el-button
        v-if="isPaused == true"
        @click="auto_play"
        style="width: 240px; margin-top: 10px; margin-left: 0"
        size="large"
        type="primary"
        >自动播放</el-button
      >
      <el-button
        v-else
        @click="pause_play"
        style="width: 240px; margin-top: 10px; margin-left: 0"
        size="large"
        type="primary"
        >暂停</el-button
      >
      <div style="display: flex; align-items: center; justify-content: center">
        <div>快</div>
        <el-slider
          style="margin: 0 10px"
          v-model="interval"
          :show-tooltip="false"
          :min="500"
          :max="1500"
        />
        <div>慢</div>
      </div>

      <el-select
        v-model="attr_show"
        s
        size="large"
        style="width: 240px; margin-bottom: 10px; margin-top: 10px"
        @change="change_attr"
      >
        <el-option
          v-for="item in attrs"
          :key="item.value"
          :label="item.label"
          :value="item"
        />
      </el-select>

      <el-input
        v-model="tmp_code"
        style="width: 178px; margin-right: 5px"
        placeholder="输入需要对比的股票代码"
        clearable
      />
      <el-button @click="add_stock" size="small">添加</el-button>
      <div class="code_container">
        <div class="code_item" v-for="(item, index) in codes" :key="index">
          {{ item.code }}
          <el-button
            v-if="index !== 0"
            :icon="CloseBold"
            style="margin-left: auto"
            @click="delete_code(item.code)"
          />
        </div>
      </div>
    </div>

    <div class="echarts-container" id="charts" ref="echartsContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { CloseBold } from "@element-plus/icons-vue";
import * as echarts from "echarts";
import axios from "axios";
import { saveAs } from "file-saver";

import { useRoute } from "vue-router";
const route = useRoute();

const SECUCODE = route.query.code;
var codes = ref([]);
var tmp_code = ref("");
var interval = ref(1000);
const echartsContainer = ref(null);
let chart = null;
const attrs = [
  { label: "每股收益", value: "BASIC_EPS" },
  { label: "营业总收入", value: "TOTAL_OPERATE_INCOME" },
  { label: "净利润", value: "PARENT_NETPROFIT" },
  { label: "每股净资产", value: "BPS" },
  { label: "净收益率", value: "WEIGHTAVG_ROE" },
  { label: "每股经营现金流量", value: "MGJYXJJE" },
  { label: "销售毛利率", value: "XSMLL" },
  { label: "货币资金", value: "MONETARYFUNDS" },
  { label: "应收账款", value: "ACCOUNTS_RECE" },
  { label: "存货", value: "INVENTORY" },
  { label: "总资产", value: "TOTAL_ASSETS" },
  { label: "应付账款", value: "ACCOUNTS_PAYABLE" },
  { label: "预收账款", value: "ADVANCE_RECEIVABLES" },
  { label: "总负债", value: "TOTAL_LIABILITIES" },
  { label: "资产负债率", value: "DEBT_ASSET_RATIO" },
  { label: "股东权益合计", value: "TOTAL_EQUITY" },
  { label: "营业支出", value: "OPERATE_COST" },
  { label: "销售费用", value: "SALE_EXPENSE" },
  { label: "管理费用", value: "MANAGE_EXPENSE" },
  { label: "财务费用", value: "FINANCE_EXPENSE" },
  { label: "营业总支出", value: "TOTAL_OPERATE_COST" },
  { label: "营业利润", value: "OPERATE_PROFIT" },
  { label: "利润总额", value: "TOTAL_PROFIT" },
  { label: "净现金流", value: "CCE_ADD" },
  { label: "经营性现金流量净额", value: "NETCASH_OPERATE" },
  { label: "投资性现金流量净额", value: "NETCASH_INVEST" },
  { label: "融资性现金流量净额", value: "NETCASH_FINANCE" },
];
var attr_show = ref(attrs[0]);

var options = ref({
  animationDuration: 800,

  title: {
    text: attr_show.value.label,
    left: "center",
    top: 50,
    textStyle: {
      fontSize: 100,
      color: "rgba(0, 0, 0, 0.3)",
    },
  },
  tooltip: {
    trigger: "axis",
  },
  legend: {
    data: [],
    itemHeight: 30,
  },
  grid: {
    left: "3%",
    right: "4%",
    bottom: "15%",
    containLabel: true,
  },
  toolbox: {
    feature: {
      saveAsImage: {},
    },
  },
  dataZoom: [
    {
      show: true,
      realtime: true,
      start: 0,
      end: 100,
    },
  ],
  xAxis: {
    type: "category",
    data: [],
  },
  yAxis: {
    type: "value",
  },
  series: [],
});

onMounted(async () => {
  tmp_code.value = SECUCODE;
  await add_stock();

  initChart();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});

const delete_code = (code) => {
  codes.value = codes.value.filter((item) => item.code != code);
  options.value.legend.data = codes.value.map((item) => item.code);
  options.value.series = codes.value.map((item) => {
    return {
      name: item.code,
      type: "line",
      smooth: true,
      data: item.value[attr_show.value.value].map((item) => item),
      areaStyle: { opacity: 0.5 },
    };
  });
  if (chart) {
    chart.setOption(options.value, true);
  }
};
const export_data = () => {
  let blob = new Blob([JSON.stringify(codes.value[0])], {
    type: "application/json",
  });
  saveAs(blob, SECUCODE + ".json");
};
let index = 0;
let timerId;
var isPaused = ref(true);

const loopWithInterval = () => {
  if (!isPaused.value) {
    if (index == attrs.length) {
      index = 0;
    }
    const item = attrs[index];
    attr_show.value = item;
    change_attr();
    index++;
    timerId = setTimeout(loopWithInterval, interval.value);
  }
};

const auto_play = () => {
  isPaused.value = false;
  clearTimeout(timerId);
  loopWithInterval();
};

const pause_play = () => {
  isPaused.value = true;
  clearTimeout(timerId);
};

const update_codes = () => {
  options.value.legend.data = codes.value.map((item) => item.code);
  let tmp = [];
  if (codes.value.length == 1) {
    for (let i = 0; i < codes.value[0].value["DATEMMDD"].length; i++) {
      let season_str;
      if (codes.value[0].value["DATEMMDD"][i] == 1) {
        season_str = "一季报";
      } else if (codes.value[0].value["DATEMMDD"][i] == 2) {
        season_str = "半年报";
      } else if (codes.value[0].value["DATEMMDD"][i] == 3) {
        season_str = "三季报";
      } else if (codes.value[0].value["DATEMMDD"][i] == 4) {
        season_str = "年报";
      } else {
        console.log("季度出错");
      }
      tmp.push(codes.value[0].value["DATAYEAR"][i] + "年" + season_str);
    }
    options.value.xAxis.data = tmp;
  }

  options.value.series = codes.value.map((item) => {
    return {
      name: item.code,
      type: "line",
      smooth: true,
      data: item.value[attr_show.value.value].map((item) => item),
      areaStyle: {},
    };
  });
  if (chart) {
    chart.setOption(options.value);
  }
};

const change_attr = () => {
  options.value.series = codes.value.map((item) => {
    return {
      name: item.code,
      type: "line",
      smooth: true,

      data: item.value[attr_show.value.value].map((item) => item),
      areaStyle: {},
    };
  });
  options.value.title.text = attr_show.value.label;
  if (chart) {
    chart.setOption(options.value);
  }
};
const add_stock = async () => {
  try {
    let tmp = tmp_code.value;
    tmp_code.value = "";
    await get_detail_data(tmp);
    update_codes();
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

const get_detail_data = async (code) => {
  try {
    const response = await axios.get("http://localhost:5000/detail", {
      params: {
        secucode: code,
      },
    });
    codes.value.push({
      code: code,
      value: response.data,
    });
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};
function initChart() {
  chart = echarts.init(echartsContainer.value);
  chart.setOption(options.value);
}
function handleResize() {
  if (chart) {
    chart.resize();
  } else {
    console.log("sorry");
  }
}
</script>

<style scoped>
.container {
  display: flex;
  width: 100%;
}
.echarts-container {
  width: 100%;

  height: 90%;
  background-color: rgb(255, 255, 255);
  border: 1px solid black;
  margin-right: 2vw;
  margin-top: 20px;
}
.option {
  padding: 20px;
  background-color: rgba(230, 230, 230, 0.34);
  width: 20vw;
}
.code_container {
  font-size: 15px;
}
.code_item {
  background-color: rgba(255, 255, 255, 0.51);
  border: 1px solid rgb(50, 50, 50);
  display: flex;
  justify-content: center;
  align-items: center;
  line-height: 40px;
  font-weight: 900;
  height: 40px;
  margin-top: 10px;
  padding-left: 20px;
  padding-right: 10px;

  color: rgb(0, 0, 0);
  border-radius: 3px;
  transition: transform 0.3s ease, background-color 0.3s ease, color 0.3s ease,
    border 0.3s ease;
}
.code_item:hover {
  transform: scale(1.0005); /* 使用 scale 放大元素 */
  color: white;
  background-color: rgb(255, 158, 23);
  border: none;
  cursor: pointer;
}
</style>
