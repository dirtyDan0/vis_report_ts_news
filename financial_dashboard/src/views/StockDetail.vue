<template>
  <el-container class="container">
    <el-aside class="aside">
      <div class="Board">
        <div class="top_pad" />
        <el-button @click="goBack" type="warning" class="bk_btn" plain
          >返回
        </el-button>
        <div>{{ SECUCODE }}</div>
        <div>{{ SECURITY_NAME_ABBR }}</div>
      </div>

      <div class="select_pad">
        <div style="width: 100%; height: 3vh">预计下一季度的每股收益为</div>
        {{ prediction }}元
      </div>
      <div class="news_header">
        近日新闻
        <p style="font-size: 13px; margin-top: 0">
          ℹ️(利涨/中立/利空标签由ai自动生成，结果仅供参考)
        </p>
      </div>
      <el-carousel
        v-if="news != ''"
        height="62vh"
        :interval="1500"
        direction="vertical"
        type="card"
        class="news"
      >
        <el-carousel-item
          v-for="item in news"
          :key="item"
          style="background-color: white; border: 1px solid rgb(187, 181, 181)"
        >
          <div
            v-if="item['cls'] === 2"
            style="
              height: 4vh;
              background-color: #cd5c5c;
              font-size: 20px;
              font-weight: 1000;
              color: white;
              text-align: center;
            "
          >
            利涨
            <h3
              style="background-color: #cd5c5c; font-size: 15px; height: 40vh"
            >
              {{ item["news"] }}
            </h3>
          </div>
          <div
            v-else-if="item['cls'] === 1"
            style="
              height: 4vh;
              background-color: #dcdcdc;
              font-size: 20px;
              font-weight: 1000;
              text-align: center;
            "
          >
            中立
            <h3 style="font-size: 15px; height: 40vh">
              {{ item["news"] }}
            </h3>
          </div>
          <div
            v-else
            style="
              height: 4vh;
              background-color: #3cb371;
              font-size: 20px;
              font-weight: 1000;
              text-align: center;
            "
          >
            利空
            <h3
              style="background-color: #3cb371; font-size: 15px; height: 40vh"
            >
              {{ item["news"] }}
            </h3>
          </div>
        </el-carousel-item>
      </el-carousel>
      <div
        v-else
        style="
          display: flex;

          justify-content: center;
          align-items: center;
          font-weight: 1000;
          font-size: 30px;
          height: 62vh;
          background: linear-gradient(to bottom right, #e06c1f, #f9d19c);
        "
      >
        <p>暂无新闻</p>
      </div>
    </el-aside>
    <el-main style="padding: 0">
      <LineChart :props="props"></LineChart>
    </el-main>
  </el-container>
</template>
<script setup>
import { onMounted, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import LineChart from "@/components/LineChart.vue";

const router = useRouter();
const route = useRoute();
const SECUCODE = route.query.code;
const SECURITY_NAME_ABBR = route.query.name;
const news = ref([]);
var props = ref({ code: SECUCODE });
const prediction = ref();

const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  updatePrediction();
  updateNews();
});
const updatePrediction = async () => {
  try {
    const response = await axios.get("http://localhost:5000/prediction", {
      params: {
        secucode: SECUCODE,
      },
    });
    prediction.value = response.data.prediction.toFixed(4);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};
const updateNews = async () => {
  try {
    const response = await axios.get("http://localhost:5000/news", {
      params: {
        secucode: SECUCODE,
      },
    });

    let _r = response.data.json_data;
    if (news.value == "empty") {
      news.value = "";
    } else {
      news.value = JSON.parse(_r);
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};
</script>
<style scoped>
.table_type {
  display: flex;
  justify-content: center;
}
.bk_btn {
  width: 80%;
  height: 3vh;
  font-weight: 500;
}
.top_pad {
  background-color: rgb(231, 127, 62);
  height: 1vh;
}
.news_header {
  background-color: rgb(255, 255, 255);
  height: 8vh;
  line-height: 4vh;
  border-top: 2px solid rgb(212, 210, 210);
  border-bottom: 2px solid rgb(212, 210, 210);
  font-weight: 600;
  font-size: large;
  text-align: center;
  display: block;
}
.news_bottom {
  background-color: rgb(255, 255, 255);
  height: 4vh;
  line-height: 4vh;
  border-top: 2px solid rgb(212, 210, 210);
  border-bottom: 2px solid rgb(212, 210, 210);
  font-weight: 600;
  font-size: large;
  text-align: center;
  display: block;
}
.news {
  background: white;
}
.select_pad {
  background-color: rgb(255, 255, 255);
  height: 10vh;
  line-height: 6vh;
  font-weight: 600;
  font-size: large;
  text-align: center;
  display: block;
  align-items: center;
}
.aside {
  width: 20vw;
  display: block;
}
.container {
  height: 100%;
  background-color: rgb(255, 255, 255);
  width: 100%;
  padding: 0 !important;
}
.Board {
  width: 100%;
  height: 12vh;
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
