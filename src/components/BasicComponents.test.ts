import { h } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'
import Alert from './Alert/Alert.vue'
import ButtonGroup from './ButtonGroup/ButtonGroup.vue'
import Container from './Container/Container.vue'
import Header from './Container/Header.vue'
import DatePicker from './DatePicker/DatePicker.vue'
import Icon from './Icon/Icon.vue'
import Link from './Link/Link.vue'
import Rate from './Rate/Rate.vue'

// 基础的组件测试

describe('basic components', () => {
  test('Alert closes and emits close event', async () => {
    const wrapper = mount(Alert, {
      props: {
        title: 'warning',
        type: 'warning',
        closable: true
      },
      global: {
        stubs: {
          ElIcon: true
        }
      }
    })

    await wrapper.get('.closeBtn').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('close')
  })

  test('ButtonGroup renders slot content', () => {
    const wrapper = mount(ButtonGroup, {
      slots: {
        default: '<button>left</button><button>right</button>'
      }
    })

    expect(wrapper.text()).toContain('left')
    expect(wrapper.text()).toContain('right')
  })

  test('Container infers vertical layout from header slot', () => {
    const wrapper = mount(Container, {
      props: {
        direction: 'vertical'
      },
      slots: {
        default: () => [h(Header), h('div', 'body')]
      }
    })

    expect(wrapper.classes()).toContain('el-container-vertical')
  })

  test('DatePicker renders a 42-cell calendar grid', () => {
    const wrapper = mount(DatePicker, {
      global: {
        stubs: {
          Icon: true
        }
      }
    })

    expect(wrapper.findAll('.calendar-content__item')).toHaveLength(42)
  })

  test('Icon passes color via CSS variable', () => {
    const wrapper = mount(Icon, {
      props: {
        icon: 'arrow-up',
        color: 'red'
      },
      global: {
        stubs: {
          FontAwesomeIcon: true
        }
      }
    })

    expect(wrapper.attributes('style')).toContain('--color: red')
  })

  test('Link emits click when enabled', async () => {
    const wrapper = mount(Link, {
      props: {
        type: 'primary'
      },
      slots: {
        default: 'docs'
      },
      global: {
        stubs: {
          ElIcon: true
        }
      }
    })

    await wrapper.get('a').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })

  test('Rate emits selected value when star is clicked', async () => {
    const wrapper = mount(Rate, {
      props: {
        nums: 2,
        max: 5
      }
    })

    await wrapper.findAll('.icon-star')[3].trigger('click')
    expect(wrapper.emitted('changeRateNums')?.[0]).toEqual([4])
  })
})
