// 站点配置

import { defineConfig } from 'vitepress'
import { containerPreview, componentPreview } from '@vitepress-demo-preview/plugin'
import { fileURLToPath, URL } from 'node:url'
// https://vitepress.dev/reference/site-config


export default defineConfig({
  // 基本信息
  title: "TinyElement",
  description: "A VitePress Site",
  // 别名
  vite: {
    resolve: {
      alias: {
        // 设置匹配符号 @ 指向 src 目录
        '@': fileURLToPath(new URL('../../src', import.meta.url))
      }
    }
  },
  // 配置导航栏和侧边栏
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    // 导航栏
    nav: [
      { text: '指南', link: '/' },
      { text: '组件', link: '/components/button' }
    ],
    // 侧边栏
    sidebar: [
      {
        text: '基础',
        items: [
          { text: '按钮 Button', link: '/components/button' },
          { text: '布局容器 Container', link: '/components/container' },
          { text: '图标 Icon', link: 'components/icon' },
          { text: '链接 Link', link: '/components/link' },
          { text: '折叠面板 Collapse', link: '/components/collapse' },
        ]
      },
      {
        text: '反馈',
        items: [
          { text: '反馈 Alert', link: '/components/alert' },
          { text: '消息提示 Message', link: '/components/Message' },
          { text: '消息弹出框 MessageBox', link: '/components/MessageBox' },
          { text: '文字提示 Tooltip', link: '/components/Tooltip' },
          { text: '下拉菜单 Dropdown', link: '/components/DropDown' }
        ]
      },
      {
        text: '数据输入',
        items: [
          { text: '开关 Switch', link: 'components/switch' },
          { text: '评分 Rate', link: 'components/rate' },
          { text: '输入框 Input', link: 'components/input' },
          { text: '选择框 Select', link: 'components/select' },
          { text: '表单 Form', link: '/components/form' },
          { text: '日期选择器 DatePicker', link: 'components/datepicker' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  },
  // 配置 Markdown 插件
  markdown: {
    config(md) {
      // 使用 @vitepress-demo-preview/plugin 插件，启用 demo 预览功能
      md.use(containerPreview)
      md.use(componentPreview)
    }
  },
  // 配置部署路径
  base: '/element-ui/'
})

