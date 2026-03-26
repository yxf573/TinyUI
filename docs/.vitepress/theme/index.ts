// 从 VitePress 的默认主题中导入 DefaultTheme

// 继承默认主题
import DefaultTheme from 'vitepress/theme'

// 引入 demo 预览组件样式
import { AntDesignContainer, ElementPlusContainer, NaiveUIContainer } from '@vitepress-demo-preview/component'
import '@vitepress-demo-preview/component/dist/style.css'
// 导入 Font Awesome 图标
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
// 自定义样式
import '../../../src/styles/index.css'
import './index.css'

library.add(fas)

// 在 enhanceApp 里注册全局组件
// 这是 VitePress 主题提供的一个钩子。
// 文档站启动时，VitePress 会先创建一个 Vue 应用实例，
// 然后调用这个函数，并把 app 传进来
export default {
  ...DefaultTheme,
  // 拿到 Vue 应用实例，然后注册全局组件
  enhanceApp({ app }) {
    // 
    app.component('demo-preview', NaiveUIContainer)
  }
}