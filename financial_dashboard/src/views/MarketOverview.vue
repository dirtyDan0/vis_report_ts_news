<template>
  <el-container class="container">
    <el-dialog v-model="dialogFormVisible" title="切换市场" width="500">
      <el-select v-model="tmp_market" :placeholder="market">
        <el-option v-for="item in markets" :label="item" :value="item" />
      </el-select>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogFormVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="
              market = tmp_market;
              dialogFormVisible = false;
              change();
            "
          >
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
    <el-aside class="aside">
      <div class="Board">
        <div class="top_pad" />
        <el-button
          type="warning"
          @click="dialogFormVisible = true"
          class="change_board_btn"
          plain
          >切换市场
        </el-button>
        <div>{{ market }}</div>
      </div>

      <div class="statistic">
        <el-table :data="statistic" :show-header="false" border>
          <el-table-column prop="name" />
          <el-table-column prop="value" />
        </el-table>
      </div>

      <div class="select_pad">
        <div style="width: 40%">报表类型</div>

        <el-select
          v-model="table_type"
          placeholder="Select"
          size="large"
          style="width: 58%"
        >
          <el-option
            v-for="item in tables_types"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </div>
      <div class="select_pad">
        <div style="width: 40%">报表年份</div>

        <el-select
          v-model="year"
          placeholder="Select"
          size="large"
          style="width: 58%"
          @change="change"
        >
          <el-option
            v-for="item in years"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </div>
      <div class="select_pad">
        <div style="width: 40%">报表季度</div>

        <el-select
          v-model="season"
          size="large"
          style="width: 58%"
          @change="change"
        >
          <el-option
            v-for="item in seasons"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </div>
      <Radar :props="props"></Radar>
    </el-aside>

    <el-main style="padding: 0; display: flex; justify-content: center">
      <el-table
        v-if="table_type === 'cpd'"
        :data="tableData"
        border
        stripe
        empty-text="数据更新中"
        style="width: 100%"
        @cell-mouse-enter="cell_hover"
        @cell-mouse-leave="cell_hover_leave"
        height="100%"
        @cell-click="handleCellClick"
      >
        <el-table-column prop="SECUCODE" width="130px">
          <template #header>
            股票代码
            <el-input
              v-if="stock_name === ''"
              v-model="secucode"
              style="width: 100%"
              size="small"
              placeholder="搜索股票代码"
              @input="search_code"
            />
            <el-input
              v-else
              v-model="secucode"
              style="width: 100%"
              size="small"
              disabled
              placeholder=""
              @input="search_code"
            />
          </template>
          <template #default="{ row }">
            <el-popover
              placement="left-end"
              :width="200"
              trigger="hover"
              content="点击复制股票代码至剪贴板"
            >
              <template #reference>
                <el-button @click="copyToClipboard(row.SECUCODE)">{{
                  row.SECUCODE
                }}</el-button>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
          prop="SECURITY_NAME_ABBR"
          label="股票简称"
          width="120px"
        >
          <template #header>
            股票简称
            <el-input
              v-if="secucode === ''"
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder="搜索股票简称"
              @input="search_name"
            />
            <el-input
              v-else
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder=""
              disabled
              @input="search_name"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="BASIC_EPS"
          :formatter="format_color"
          label="每股收益（元）"
        >
        </el-table-column>
        <el-table-column label="营业总收入">
          <el-table-column
            prop="TOTAL_OPERATE_INCOME"
            label="营业总收入（元）"
            :formatter="format"
          />
          <el-table-column
            prop="YSTZ"
            :formatter="format_color"
            label="同比增长（%）"
          />
          <el-table-column
            prop="YSHZ"
            :formatter="format_color"
            label="季度环比增长（%）"
          />
        </el-table-column>
        <el-table-column label="净利润">
          <el-table-column
            prop="PARENT_NETPROFIT"
            label="净利润（元）"
            :formatter="format_color"
          />
          <el-table-column
            prop="SJLTZ"
            :formatter="format_color"
            label="同比增长（%）"
          />
          <el-table-column
            prop="SJLHZ"
            :formatter="format_color"
            label="季度环比增长（%）"
          />
        </el-table-column>
        <el-table-column
          prop="BPS"
          label="每股净资产（元）"
          :formatter="format"
        />
        <el-table-column
          prop="WEIGHTAVG_ROE"
          label="净资产收益率（%）"
          :formatter="format_color"
        />
        <el-table-column
          prop="MGJYXJJE"
          label="每股经营现金流量（元）"
          :formatter="format_color"
        />
        <el-table-column
          prop="XSMLL"
          label="销售毛利率（%）"
          :formatter="format_color"
        />
        <el-table-column prop="INDUSTRY_NAME" label="所处行业" />
      </el-table>
      <el-table
        v-else-if="table_type === 'balance'"
        :data="tableData"
        border
        stripe
        empty-text="数据更新中"
        style="width: 100%"
        @cell-mouse-enter="cell_hover"
        @cell-mouse-leave="cell_hover_leave"
        height="100%"
        @cell-click="handleCellClick"
      >
        <el-table-column prop="SECUCODE" width="130px">
          <template #header>
            股票代码
            <el-input
              v-if="stock_name === ''"
              v-model="secucode"
              style="width: 100%"
              size="small"
              placeholder="搜索股票代码"
              @input="search_code"
            />
            <el-input
              v-else
              v-model="secucode"
              style="width: 100%"
              size="small"
              disabled
              placeholder=""
              @input="search_code"
            />
          </template>
          <template #default="{ row }">
            <el-popover
              placement="left-end"
              :width="200"
              trigger="hover"
              content="点击复制股票代码至剪贴板"
            >
              <template #reference>
                <el-button @click="copyToClipboard(row.SECUCODE)">{{
                  row.SECUCODE
                }}</el-button>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
          prop="SECURITY_NAME_ABBR"
          label="股票简称"
          width="120px"
          ><template #header>
            股票代码
            <el-input
              v-if="secucode === ''"
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder="搜索股票简称"
              @input="search_name"
            />
            <el-input
              v-else
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder=""
              disabled
              @input="search_name"
            /> </template></el-table-column
        ><el-table-column label="资产">
          <el-table-column
            prop="MONETARYFUNDS"
            label="货币资金（元）"
            :formatter="format"
          />
          <el-table-column
            prop="ACCOUNTS_RECE"
            label="应收账款（元）"
            :formatter="format"
          />
          <el-table-column
            prop="INVENTORY"
            label="存货（元）"
            :formatter="format"
          />
          <el-table-column
            prop="TOTAL_ASSETS"
            label="总资产（元）"
            :formatter="format"
          />
          <el-table-column
            prop="TOTAL_ASSETS_RATIO"
            :formatter="format_color"
            label="总资产同比（%）"
          />
        </el-table-column>
        <el-table-column label="负债">
          <el-table-column
            prop="ACCOUNTS_PAYABLE"
            label="应付账款（元）"
            :formatter="format"
          />
          <el-table-column
            prop="ADVANCE_RECEIVABLES"
            label="预收账款（元）"
            :formatter="format"
          />
          <el-table-column
            prop="TOTAL_LIABILITIES"
            label="总负债（元）"
            :formatter="format"
          />
          <el-table-column
            prop="TOTAL_LIAB_RATIO"
            :formatter="format_color"
            label="总负债同比（%）"
          />
        </el-table-column>
        <el-table-column
          prop="DEBT_ASSET_RATIO"
          :formatter="format_color"
          label="资产负债率（%）"
        />
        <el-table-column
          prop="TOTAL_EQUITY"
          label="股东权益合计（元）"
          :formatter="format"
        />
      </el-table>
      <el-table
        v-else-if="table_type === 'income'"
        :data="tableData"
        border
        stripe
        empty-text="数据更新中"
        style="width: 100%"
        @cell-mouse-enter="cell_hover"
        @cell-mouse-leave="cell_hover_leave"
        height="100%"
        @cell-click="handleCellClick"
      >
        <el-table-column prop="SECUCODE" width="130px">
          <template #header>
            股票代码
            <el-input
              v-if="stock_name === ''"
              v-model="secucode"
              style="width: 100%"
              size="small"
              placeholder="搜索股票代码"
              @input="search_code"
            />
            <el-input
              v-else
              v-model="secucode"
              style="width: 100%"
              size="small"
              disabled
              placeholder=""
              @input="search_code"
            />
          </template>
          <template #default="{ row }">
            <el-popover
              placement="left-end"
              :width="200"
              trigger="hover"
              content="点击复制股票代码至剪贴板"
            >
              <template #reference>
                <el-button @click="copyToClipboard(row.SECUCODE)">{{
                  row.SECUCODE
                }}</el-button>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
          prop="SECURITY_NAME_ABBR"
          label="股票简称"
          width="120px"
          ><template #header>
            股票代码
            <el-input
              v-if="secucode === ''"
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder="搜索股票简称"
              @input="search_name"
            />
            <el-input
              v-else
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder=""
              disabled
              @input="search_name"
            /> </template
        ></el-table-column>
        <el-table-column
          prop="PARENT_NETPROFIT"
          label="净利润（元）"
          :formatter="format"
        />
        <el-table-column
          prop="PARENT_NETPROFIT_RATIO"
          label="净利润同比（%）"
          :formatter="format_color"
        />
        <el-table-column
          prop="TOTAL_OPERATE_INCOME"
          label="营业总收入（元）"
          :formatter="format"
        />
        <el-table-column
          prop="TOI_RATIO"
          label="营业总收入同比（%）"
          :formatter="format_color"
        />
        <el-table-column label="营业总支出">
          <el-table-column
            prop="OPERATE_COST"
            label="营业支出（元）"
            :formatter="format"
          />
          <el-table-column
            prop="SALE_EXPENSE"
            label="销售费用（元）"
            :formatter="format"
          />
          <el-table-column
            prop="MANAGE_EXPENSE"
            label="管理费用（元）"
            :formatter="format"
          />
          <el-table-column
            prop="FINANCE_EXPENSE"
            label="财务费用（元）"
            :formatter="format"
          />
          <el-table-column
            prop="TOTAL_OPERATE_COST"
            label="营业总支出（元）"
            :formatter="format"
          />
        </el-table-column>
        <el-table-column
          prop="OPERATE_PROFIT"
          label="营业利润（元）"
          :formatter="format"
        />
        <el-table-column
          prop="TOTAL_PROFIT"
          label="利润总额（元）"
          :formatter="format"
        />
      </el-table>
      <el-table
        v-else-if="table_type === 'cashflow'"
        :data="tableData"
        border
        stripe
        empty-text="数据更新中"
        style="width: 100%"
        @cell-mouse-enter="cell_hover"
        @cell-mouse-leave="cell_hover_leave"
        height="100%"
        @cell-click="handleCellClick"
      >
        <el-table-column prop="SECUCODE" width="130px">
          <template #header>
            股票代码
            <el-input
              v-if="stock_name === ''"
              v-model="secucode"
              style="width: 100%"
              size="small"
              placeholder="搜索股票代码"
              @input="search_code"
            />
            <el-input
              v-else
              v-model="secucode"
              style="width: 100%"
              size="small"
              disabled
              placeholder=""
              @input="search_code"
            />
          </template>
          <template #default="{ row }">
            <el-popover
              placement="left-end"
              :width="200"
              trigger="hover"
              content="点击复制股票代码至剪贴板"
            >
              <template #reference>
                <el-button @click="copyToClipboard(row.SECUCODE)">{{
                  row.SECUCODE
                }}</el-button>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
          prop="SECURITY_NAME_ABBR"
          label="股票简称"
          width="120px"
          ><template #header>
            股票代码
            <el-input
              v-if="secucode === ''"
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder="搜索股票简称"
              @input="search_name"
            />
            <el-input
              v-else
              v-model="stock_name"
              style="width: 100%"
              size="small"
              placeholder=""
              disabled
              @input="search_name"
            /> </template
        ></el-table-column>
        <el-table-column label="净现金流">
          <el-table-column
            prop="CCE_ADD"
            label="净现金流（元）"
            :formatter="format"
          />
          <el-table-column
            prop="CCE_ADD_RATIO"
            label="同比增长（%）"
            :formatter="format_color"
          />
        </el-table-column>
        <el-table-column label="经营性现金流">
          <el-table-column
            prop="NETCASH_OPERATE"
            label="现金流量净额（元）"
            :formatter="format"
          />
          <el-table-column
            prop="NETCASH_OPERATE_RATIO"
            label="净现金流占比（%）"
            :formatter="format_color"
          />
          />
        </el-table-column>
        <el-table-column label="投资性现金流">
          <el-table-column
            prop="NETCASH_INVEST"
            label="现金流量净额（元）"
            :formatter="format"
          />
          <el-table-column
            prop="NETCASH_INVEST_RATIO"
            label="净现金流占比（%）"
            :formatter="format_color"
          />
          />
        </el-table-column>
        <el-table-column label="融资性现金流">
          <el-table-column
            prop="NETCASH_FINANCE"
            label="现金流量净额（元）"
            :formatter="format"
          />
          <el-table-column
            prop="NETCASH_FINANCE_RATIO"
            label="净现金流占比（%）"
            :formatter="format_color"
          />
          />
        </el-table-column>
      </el-table>
      <el-pagination
        layout="prev, pager, next, jumper"
        :page-size="10"
        :total="counts"
        background
        style="position: fixed; z-index: 10; bottom: 10px; margin: auto"
        @current-change="change_page"
      />
    </el-main>
  </el-container>
</template>
<script setup>
import { ref, onMounted, h } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";
import Radar from "@/components/Radar.vue";
import { useRouter } from "vue-router";

const router = useRouter();

var table_type = ref("cpd");
var year = ref("2023");
var season = ref(3);
var market = ref("上交所主板");
var tmp_market = ref("");
var tableData = ref([]);
var tableData_all = ref([]);
var page = ref(1);
var means = ref([]);
var means_industry = ref([]);

var maxEps = ref("计算中");
var minEps = ref("计算中");
var avgEps = ref("计算中");
var counts = ref(0);
var secucode = ref("");
var hover_row = ref("");
var stock_name = ref("");
const years = [];
var dialogFormVisible = ref(false);
const markets = [
  "上交所主板",
  "深交所创业板",
  "深交所主板",
  "上交所风险警示板",
  "深交所风险警示板",
];
const handleCellClick = (event, column) => {
  if (column.property != "SECUCODE") {
    router.push({
      path: "/stockdetail",
      query: {
        code: hover_row.value["SECUCODE"],
        name: hover_row.value["SECURITY_NAME_ABBR"],
      },
    });
  }
};

const copyToClipboard = (text) => {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  ElMessage({
    message: "股票代码已复制",
    type: "success",
  });
};
const formatNumber = (value) => {
  let absValue = Math.abs(value);
  if (absValue >= 1000000000000) {
    return `${(value / 1000000000000).toFixed(2)} 万亿`;
  } else if (absValue >= 100000000000) {
    return `${(value / 100000000000).toFixed(2)} 千亿`;
  } else if (absValue >= 100000000) {
    return `${(value / 100000000).toFixed(2)} 亿`;
  } else if (absValue >= 10000) {
    return `${(value / 10000).toFixed(2)} 万`;
  } else {
    return value.toFixed(2).toString();
  }
};

const format = (row, column, cellValue) => {
  if (cellValue == null || cellValue == "/") {
    return "/";
  }
  return formatNumber(cellValue);
};
const format_color = (row, column, cellValue) => {
  // 定义正数的颜色为红色，负数的颜色为绿色
  if (cellValue == null || cellValue == "/") {
    return h("span", "/");
  }

  let color = "black";
  if (cellValue > 0) {
    color = "red";
  } else if (cellValue < 0) {
    color = "green";
  } else {
    return h("span", { style: `font-weight:1000` }, formatNumber(cellValue));
  }

  return h(
    "span",
    { style: `color: ${color};font-weight:1000` },
    formatNumber(cellValue)
  );
};

for (let year = 2023; year >= 2010; year--) {
  years.push(year);
}
var seasons = ref([1, 2, 3]);
var props = ref({
  hover_row: hover_row,
  table_type: table_type,
  means: means,
  means_industry: means_industry,
});
const tables_types = [
  {
    value: "cpd",
    label: "业绩报表",
  },
  {
    value: "balance",
    label: "资产负债表",
  },
  {
    value: "income",
    label: "利润表",
  },
  {
    value: "cashflow",
    label: "现金流量表",
  },
];

const cell_hover = (row, column, cell, event) => {
  props.value["hover_row"] = row;
};
const cell_hover_leave = (row, column, cell, event) => {
  props.value["hover_row"] = "";
};
const change_page = async (value) => {
  page.value = value;

  tableData.value = tableData_all.value.slice(
    (page.value - 1) * 10,
    page.value * 10
  );
};

const search_code = (code) => {
  if (code == "") {
    tableData.value = tableData_all.value.slice(
      page.value - 1,
      page.value - 1 + 10
    );
    counts.value = tableData_all.value.length;
  } else {
    let res = [];
    code = code.toUpperCase();
    for (const item of tableData_all.value) {
      if (item["SECUCODE"].includes(code)) {
        res.push(item);
      }
    }
    tableData.value = res;
    counts.value = res.length;
  }
};

const search_name = (name) => {
  if (name == "") {
    tableData.value = tableData_all.value.slice(
      page.value - 1,
      page.value - 1 + 10
    );
    counts.value = tableData_all.value.length;
  } else {
    let res = [];
    for (const item of tableData_all.value) {
      if (item["SECURITY_NAME_ABBR"].includes(name)) {
        res.push(item);
      }
    }
    tableData.value = res;
    counts.value = res.length;
  }
};
const change = async () => {
  counts.value = 0;
  maxEps.value = "计算中";
  minEps.value = "计算中";
  avgEps.value = "计算中";

  if (year.value == 2023) {
    seasons.value = [1, 2, 3];
  } else {
    seasons.value = [1, 2, 3, 4];
  }
  ElMessage({
    message: "更新数据中",
  });
  await updateData();
  ElMessage({
    message: "数据更新成功",
    type: "success",
  });
};
const updateData = async () => {
  try {
    tableData.value = [];
    const response = await axios.get("http://localhost:5000/reportdata", {
      params: {
        market: market.value,
        year: year.value,
        season: season.value,
      },
    });

    means.value = JSON.parse(response.data.mean)[0];
    means_industry.value = JSON.parse(response.data.means_industry);
    tableData_all.value = JSON.parse(response.data.json_data);

    counts.value = tableData_all.value.length;

    let epsValues = tableData_all.value.map((obj) => obj.BASIC_EPS);
    maxEps.value = Math.max(...epsValues).toFixed(4);
    minEps.value = Math.min(...epsValues).toFixed(4);
    avgEps.value = (
      epsValues.reduce((a, b) => a + b, 0) / epsValues.length
    ).toFixed(4);
    tableData.value = tableData_all.value.slice(
      page.value - 1,
      page.value - 1 + 10
    );
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};
onMounted(change);
const statistic = [
  {
    name: "股票数量",
    value: counts,
  },
  {
    name: "最高每股收益",
    value: maxEps,
  },
  {
    name: "最低每股收益",
    value: minEps,
  },
  {
    name: "平均每股收益",
    value: avgEps,
  },
];
</script>
<style scoped>
.table_type {
  display: flex;
  justify-content: center;
}
.change_board_btn {
  width: 80%;
  height: 3vh;
  font-weight: 500;
}
.top_pad {
  background-color: rgb(231, 127, 62);
  height: 1vh;
}
.select_pad {
  background-color: rgb(255, 255, 255);
  height: 5vh;
  line-height: 5vh;
  font-weight: 600;
  text-align: center;
  display: flex;
  align-items: center;
}
.aside {
  width: 20vw;
}
.container {
  height: 100%;
  width: 100%;
  padding: 0 !important;
}
.Board {
  width: 100%;
  height: 10vh;
  background-color: rgb(255, 255, 255);
  font-size: 25px;
  text-align: center; /* 文本水平居中 */
  line-height: 4vh;
  color: rgb(0, 0, 0);
  font-weight: 1000;
  text-shadow: 0px 0px 1px rgba(0, 0, 0, 0.5);
  font-family: "Microsoft YaHei", sans-serif;
}

@media (max-width: 1000px) {
  .container {
    display: block;
  }
  .aside {
    background-color: rgb(200, 194, 194);
    width: 100%;
  }
}
</style>
