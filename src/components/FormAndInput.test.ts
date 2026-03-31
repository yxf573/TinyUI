import { defineComponent, reactive } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'
import Form from './Form/Form.vue'
import FormItem from './Form/FormItem.vue'
import Input from './Input/Input.vue'
import { formItemContextKey } from './Form/types'


// 表单和input框的测试

describe('form and input', () => {
  test('Input emits model updates', async () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: ''
      },
      global: {
        provide: {
          [formItemContextKey as symbol]: {
            validate: vi.fn(() => Promise.resolve(true))
          }
        },
        stubs: {
          ElIcon: true
        }
      }
    })

    await wrapper.get('input').setValue('hello')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['hello'])
    expect(wrapper.emitted('input')?.[0]).toEqual(['hello'])
  })

  test('Form validate rejects invalid model and resolves after update', async () => {
    const Demo = defineComponent({
      components: {
        Form,
        FormItem,
        Input
      },
      setup() {
        const model = reactive({
          name: ''
        })
        const rules = {
          name: [
            { required: true, message: 'name is required', trigger: 'blur' }
          ]
        }

        return {
          model,
          rules
        }
      },
      template: `
        <Form ref="formRef" :model="model" :rules="rules">
          <FormItem label="Name" prop="name">
            <Input v-model="model.name" />
          </FormItem>
        </Form>
      `
    })

    const wrapper = mount(Demo, {
      global: {
        stubs: {
          ElIcon: true
        }
      }
    })

    const formWrapper = wrapper.findComponent(Form)
    await expect(((formWrapper.vm as unknown) as { validate: () => Promise<boolean> }).validate()).rejects.toBeTruthy()

    await wrapper.get('input').setValue('tiny-ui')
    await expect(((formWrapper.vm as unknown) as { validate: () => Promise<boolean> }).validate()).resolves.toBe(true)
  })
})
