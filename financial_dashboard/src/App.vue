<script setup>
import { RouterView } from "vue-router";
</script>

<template>
  <div id="app">
    <el-container style="height: 100%">
      <el-header class="custom-header"
        >上市公司财报数据交互可视分析系统
        <span style="position: fixed; right: 10%">投资有风险，入市需谨慎</span>
      </el-header>
      <el-main class="router-view">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
html,
body {
  margin: 0 !important;
  padding: 0;
}

/* 如果您想要完全填充整个视口，可以设置为100% */
#app {
  width: 100%;
  height: 100vh;
  margin: 0;
  background-color: #ffffff;
}

.custom-header {
  white-space: nowrap;
  height: 6vh;
  backdrop-filter: blur(20px) brightness(0.8) saturate(180%);
  -webkit-backdrop-filter: blur(20px) brightness(0.8) saturate(180%);
  color: rgb(28, 24, 24);
  font-weight: 1000;
  text-shadow: 0px 0px 1px rgba(59, 52, 52, 0.5);
  font-family: "Microsoft YaHei", sans-serif;
  text-align: left;
  line-height: 6vh;
  font-size: 25px;
  background-color: #ffffff;
  border-bottom: 1px solid rgb(200, 194, 194);
}

.router-view {
  width: 100%;
  height: 100%;
  padding: 0;
}
</style>
