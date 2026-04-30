import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'
import router from './router'
import './assets/main.css'


// 创建应用
const app = createApp(App)

// 安装插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 挂载应用
app.mount('#app')