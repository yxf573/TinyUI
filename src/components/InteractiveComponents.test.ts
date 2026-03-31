import { defineComponent, h, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'

// 交互组件的测试


const mocks = vi.hoisted(() => ({
  createPopper: vi.fn(() => ({
    destroy: vi.fn()
  }))
}))

vi.mock('@popperjs/core', () => ({
  createPopper: mocks.createPopper
}))

import Collapse from './Collapse/Collapse.vue'
import CollapseItem from './Collapse/CollapseItem.vue'
import Dialog from './Dialog/Dialog.vue'
import Dropdown from './Dropdown/Dropdown.vue'
import Select from './Select/Select.vue'
import Switch from './Switch/Switch.vue'
import Tooltip from './Tooltip/Tooltip.vue'

const TooltipStub = defineComponent({
  name: 'Tooltip',
  setup(_, { slots, expose }) {
    const visible = ref(true)

    expose({
      show: () => {
        visible.value = true
      },
      hide: () => {
        visible.value = false
      }
    })

    return () => h('div', [
      slots.default?.(),
      visible.value ? slots.content?.() : null
    ])
  }
})

const InputStub = defineComponent({
  name: 'ElInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'input'],
  setup(props, { emit, slots }) {
    return () => h('div', [
      h('input', {
        value: props.modelValue,
        placeholder: props.placeholder,
        onInput: (event: Event) => {
          const value = (event.target as HTMLInputElement).value
          emit('update:modelValue', value)
          emit('input', value)
        }
      }),
      slots.suffix?.()
    ])
  }
})

describe('interactive components', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  test('Collapse toggles active items', async () => {
    const wrapper = mount(Collapse, {
      props: {
        modelValue: []
      },
      slots: {
        default: () => [
          h(CollapseItem, { name: 'a', title: 'A' }, () => 'content-a')
        ]
      },
      global: {
        stubs: {
          ElIcon: true
        }
      }
    })

    await wrapper.get('.el-collapse-item-title').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([['a']])
  })

  test('Dialog emits model update on close and supports dragging', async () => {
    const wrapper = mount(Dialog, {
      props: {
        modelValue: true,
        title: 'dialog',
        draggable: true
      },
      slots: {
        default: 'content'
      },
      global: {
        stubs: {
          ElIcon: true
        }
      }
    })

    await wrapper.get('.el-dialog__header').trigger('mousedown', {
      clientX: 100,
      clientY: 100
    })
    window.dispatchEvent(new MouseEvent('mousemove', {
      clientX: 150,
      clientY: 160
    }))
    await wrapper.vm.$nextTick()

    expect(wrapper.get('.el-dialog__content').attributes('style')).toContain('translate(50px, 60px)')

    await wrapper.get('.el-dialog__headerbtn').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
  })

  test('Dropdown emits selected menu item', async () => {
    const wrapper = mount(Dropdown, {
      props: {
        menuOptions: [
          { key: '1', label: 'First' }
        ]
      },
      slots: {
        default: 'trigger'
      },
      global: {
        stubs: {
          Tooltip: TooltipStub
        }
      }
    })

    await wrapper.get('.el-dropdown__item').trigger('click')
    expect(wrapper.emitted('select')?.[0]?.[0]).toMatchObject({ key: '1', label: 'First' })
  })

  test('Select supports selecting and clearing options', async () => {
    const wrapper = mount(Select, {
      props: {
        modelValue: '',
        clearable: true,
        options: [
          { label: 'Option A', value: 'a' },
          { label: 'Option B', value: 'b' }
        ]
      },
      global: {
        stubs: {
          ElTooltip: TooltipStub,
          ElInput: InputStub,
          ElIcon: true,
          RenderVnode: defineComponent({
            props: {
              vNode: {
                type: [String, Object],
                required: true
              }
            },
            setup(props) {
              return () => h('span', props.vNode as string)
            }
          })
        }
      }
    })

    await wrapper.get('.el-select').trigger('click')
    await wrapper.findAll('.el-select-menu-item')[0].trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['a'])

    await wrapper.get('.el-select').trigger('mouseenter')
    await wrapper.get('.el-input-clear').trigger('click')
    expect(wrapper.emitted('clear')).toBeTruthy()
  })

  test('Switch toggles between active and inactive values', async () => {
    const wrapper = mount(Switch, {
      props: {
        modelValue: false,
        activeValue: true,
        inactiveValue: false
      }
    })

    await wrapper.get('.el-switch').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([true])
    expect(wrapper.emitted('change')?.[0]).toEqual([true])
  })

  test('Tooltip opens on click trigger', async () => {
    const wrapper = mount(Tooltip, {
      props: {
        content: 'tooltip-body',
        trigger: 'click'
      },
      slots: {
        default: '<button>trigger</button>'
      }
    })

    await wrapper.get('.el-tooltip__trigger').trigger('click')
    vi.runAllTimers()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('tooltip-body')
    expect(mocks.createPopper).toHaveBeenCalled()
  })
})
