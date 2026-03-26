// 测试

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from './Button.vue'
import ElIcon from '../Icon/Icon.vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

describe('Button.vue', () => {
  // 基础渲染
  test('basic button', () => {
    // 挂载
    const wrapper = mount(Button, {
      // 传递 props 和 slots
      props: {
        type: 'primary'
      },
      slots: {
        default: 'button'
      }
    })
    console.log(wrapper.html())
    // slot get|find
    // 断言 类别名是否包含
    expect(wrapper.classes()).toContain('el-button--primary')
    // 是否存在button元素
    expect(wrapper.get('button').text()).toBe('button')
    // events
    // 点击事件是否正常
    wrapper.get('button').trigger('click')
    console.log(wrapper.emitted())
    expect(wrapper.emitted()).toHaveProperty('click')
  })
  // 禁用
  test('disable button', () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true,
      },
      slots: {
        default: 'disabled'
      }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.find('button').element.disabled).toBeDefined()
    wrapper.get('button').trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })
  // 图标
  test('icon', () => {
    const wrapper = mount(Button, {
      props: {
        icon: 'arrow-up'
      },
      slots: {
        default: 'icon'
      },
      global: {
        stubs: ['FontAwesomeIcon']
      }
    })
    console.log(wrapper.html())
    const iconElement = wrapper.findComponent(FontAwesomeIcon)
    expect(iconElement.exists).toBeTruthy()
    expect(iconElement.attributes('icon')).toBe('arrow-up')
  })
  // loading
  test('loading', () => {
    const wrapper = mount(Button, {
      props: {
        loading: true
      },
      slots: {
        default: 'loading'
      },
      global: {
        stubs: ['ElIcon']
      }
    })
    console.log(wrapper.html())
    const iconElement = wrapper.findComponent(ElIcon)
    expect(iconElement.exists()).toBeTruthy()
    expect(iconElement.attributes('icon')).toBe('spinner')
    expect(wrapper.attributes('disabled')).toBeDefined()
  })
})