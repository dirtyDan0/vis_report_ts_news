<template>
  <div class="container">
    <div class="echarts-container" id="charts" ref="echartsContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, watch } from "vue";
import * as echarts from "echarts";
const echartsContainer = ref(null);

let chart = null;
let _props = defineProps(["props"]);
const props = ref(_props["props"]);
var show_attrs = [];
var title = "市场均值";
var show_data = [];
var row = [];
var industry = ref("");
var industry_json;

watch(props.value, (newData, oldData) => {
  industry.value = props.value["hover_row"]["INDUSTRY_NAME"];
  if (props.value["table_type"] == "cpd") {
    show_attrs = [
      { name: "每股收益" },
      { name: "营业\n总收入" },
      { name: "净利润" },
      { name: "每股净资产" },
      { name: "每股经营\n现金流量" },
    ];
    show_data = [
      {
        value: [
          props.value["means"]["BASIC_EPS"],
          props.value["means"]["TOTAL_OPERATE_INCOME"],
          props.value["means"]["PARENT_NETPROFIT"],
          props.value["means"]["BPS"],
          props.value["means"]["MGJYXJJE"],
        ],
        name: "市场均值",
        areaStyle: {
          color: "rgba(87, 86, 241, 0.1)",
        },
      },
    ];
    if (props.value["hover_row"] != "") {
      industry_json = {
        value: [
          props.value["means_industry"][industry.value]["BASIC_EPS"],
          props.value["means_industry"][industry.value]["TOTAL_OPERATE_INCOME"],
          props.value["means_industry"][industry.value]["PARENT_NETPROFIT"],
          props.value["means_industry"][industry.value]["BPS"],
          props.value["means_industry"][industry.value]["MGJYXJJE"],
        ],
        name: industry.value + "行业均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.5)",
        },
      };
    }

    row = [
      props.value["hover_row"]["BASIC_EPS"],
      props.value["hover_row"]["TOTAL_OPERATE_INCOME"],
      props.value["hover_row"]["PARENT_NETPROFIT"],
      props.value["hover_row"]["BPS"],
      props.value["hover_row"]["MGJYXJJE"],
    ];
  } else if (props.value["table_type"] == "balance") {
    show_attrs = [
      { name: "应收账款" },
      { name: "总资产" },
      { name: "应付账款" },
      { name: "总负债" },
      { name: "股东权益\n合计" },
    ];
    show_data = [
      {
        value: [
          props.value["means"]["ACCOUNTS_RECE"],
          props.value["means"]["TOTAL_ASSETS"],
          props.value["means"]["ACCOUNTS_PAYABLE"],
          props.value["means"]["TOTAL_LIABILITIES"],
          props.value["means"]["TOTAL_EQUITY"],
        ],
        name: "市场均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.6)",
        },
      },
    ];
    if (props.value["hover_row"] != "") {
      industry_json = {
        value: [
          props.value["means_industry"][industry.value]["ACCOUNTS_RECE"],
          props.value["means_industry"][industry.value]["TOTAL_ASSETS"],
          props.value["means_industry"][industry.value]["ACCOUNTS_PAYABLE"],
          props.value["means_industry"][industry.value]["TOTAL_LIABILITIES"],
          props.value["means_industry"][industry.value]["TOTAL_EQUITY"],
        ],
        name: industry.value + "行业均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.5)",
        },
      };
    }

    row = [
      props.value["hover_row"]["ACCOUNTS_RECE"],
      props.value["hover_row"]["TOTAL_ASSETS"],
      props.value["hover_row"]["ACCOUNTS_PAYABLE"],
      props.value["hover_row"]["TOTAL_LIABILITIES"],
      props.value["hover_row"]["TOTAL_EQUITY"],
    ];
  } else if (props.value["table_type"] == "income") {
    show_attrs = [
      { name: "净利润" },
      { name: "营业总收入" },
      { name: "营业总支出" },
      { name: "营业利润" },
      { name: "利润总额" },
    ];
    show_data = [
      {
        value: [
          props.value["means"]["PARENT_NETPROFIT"],
          props.value["means"]["TOTAL_OPERATE_INCOME"],
          props.value["means"]["TOTAL_OPERATE_COST"],
          props.value["means"]["OPERATE_PROFIT"],
          props.value["means"]["TOTAL_PROFIT"],
        ],
        name: "市场均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.6)",
        },
      },
    ];
    if (props.value["hover_row"] != "") {
      industry_json = {
        value: [
          props.value["means_industry"][industry.value]["PARENT_NETPROFIT"],
          props.value["means_industry"][industry.value]["TOTAL_OPERATE_INCOME"],
          props.value["means_industry"][industry.value]["TOTAL_OPERATE_COST"],
          props.value["means_industry"][industry.value]["OPERATE_PROFIT"],
          props.value["means_industry"][industry.value]["TOTAL_PROFIT"],
        ],
        name: industry.value + "行业均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.5)",
        },
      };
    }

    row = [
      props.value["hover_row"]["PARENT_NETPROFIT"],
      props.value["hover_row"]["TOTAL_OPERATE_INCOME"],
      props.value["hover_row"]["TOTAL_OPERATE_COST"],
      props.value["hover_row"]["OPERATE_PROFIT"],
      props.value["hover_row"]["TOTAL_PROFIT"],
    ];
  } else if (props.value["table_type"] == "cashflow") {
    show_attrs = [
      { name: "净现金流" },
      { name: "经营性现金\n流量净额" },
      { name: "投资性现金\n流量净额" },
      { name: "融资性现金\n流量净额" },
    ];
    show_data = [
      {
        value: [
          props.value["means"]["CCE_ADD"],
          props.value["means"]["NETCASH_OPERATE"],
          props.value["means"]["NETCASH_INVEST"],
          props.value["means"]["NETCASH_FINANCE"],
        ],
        name: "市场均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.6)",
        },
      },
    ];
    if (props.value["hover_row"] != "") {
      industry_json = {
        value: [
          props.value["means_industry"][industry.value]["CCE_ADD"],
          props.value["means_industry"][industry.value]["NETCASH_OPERATE"],
          props.value["means_industry"][industry.value]["NETCASH_INVEST"],
          props.value["means_industry"][industry.value]["NETCASH_FINANCE"],
        ],
        name: industry.value + "行业均值",
        areaStyle: {
          color: "rgba(255, 228, 52, 0.5)",
        },
      };
    }

    row = [
      props.value["hover_row"]["CCE_ADD"],
      props.value["hover_row"]["NETCASH_OPERATE"],
      props.value["hover_row"]["NETCASH_INVEST"],
      props.value["hover_row"]["NETCASH_FINANCE"],
    ];
  }

  if (props.value["hover_row"] != "") {
    show_data = show_data.concat([
      industry_json,
      {
        value: row,
        name: props.value["hover_row"]["SECUCODE"],
      },
    ]);
    title = "市场均值 对比 " + props.value["hover_row"]["SECUCODE"];
  } else {
    title = "市场均值";
    row = [];
  }

  initChart();
});

onMounted(async () => {
  watch(props.value, (newData, oldData) => {
    initChart();
  });
  window.addEventListener("resize", handleResize);
});
async function initChart() {
  if (chart) {
    chart.dispose();
  }

  chart = echarts.init(echartsContainer.value);
  const options = {
    animation: false,

    color: ["#5756f1", "#FFE434", "#f156a3"],
    title: {
      text: title,
      left: "center",
      top: 30,
    },
    legend: { top: 65 },
    radar: {
      indicator: show_attrs,
      center: ["50%", "60%"],
      radius: 90,
      startAngle: 90,
      splitNumber: 4,
      shape: "circle",
      axisName: {
        formatter: "{value}",
        color: "#428BD4",
        fontSize: 14,
      },
      splitArea: {
        areaStyle: {
          color: ["#77EADF", "#26C3BE", "#64AFE9", "#428BD4"],
          shadowColor: "rgba(0, 0, 0, 0.2)",
          shadowBlur: 10,
        },
      },
      axisLine: {
        lineStyle: {
          color: "rgba(211, 253, 250, 0.8)",
        },
      },
      splitLine: {
        lineStyle: {
          color: "rgba(211, 253, 250, 0.8)",
        },
      },
    },

    series: [
      {
        type: "radar",
        emphasis: {
          lineStyle: {
            width: 4,
          },
        },
        data: show_data,
      },
    ],
  };

  chart.setOption(options);
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
  width: 100%;
  height: 50vh !important;
}
.echarts-container {
  width: 100% !important;
  height: 50vh !important;
  background-color: white;
  border-top: 3px solid rgb(224, 224, 224);
}
</style>
