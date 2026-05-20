# TinyElement 组件实现流程与面试官深挖题库

## 1. 这份文档怎么用

这份文档专门回答两个问题：

1. 每个组件在源码里到底是怎么实现出来的。
2. 如果我是前端面试官，我会顺着这些源码继续深挖哪些问题。

建议你的使用方法是：

- 先用 [INTERVIEW_PREP.md](./INTERVIEW_PREP.md) 讲项目总览。
- 再用 [INTERVIEW_PREP_FULL.md](./INTERVIEW_PREP_FULL.md) 讲组件问答和技术栈深挖。
- 最后用这份文档去训练“顺着源码讲实现流程”和“接住代码级追问”。

这份文档的写法固定为 5 个部分：

- 组件职责
- 实现流程
- 面试官会追问什么
- 回答方向
- 代码层可优化点

## 2. 面试官看组件源码时最常追的 5 类问题

在进入具体组件前，你先记住一个规律。面试官顺源码往下问，通常不会乱问，基本都落在下面 5 类：

1. 这个组件的状态是谁在维护，为什么这样设计？
2. 这个组件和外部是怎么通信的？
3. 为什么要这样拆，而不是写在一起？
4. 这个实现有没有边界问题、性能问题或可维护性问题？
5. 如果继续迭代，你会怎么做得更像成熟组件库？

你回答时也尽量按这个顺序来。

---

## 3. 基础类组件

## 3.1 Button

### 组件职责

Button 是最基础的交互组件，负责统一按钮的类型、尺寸、图标、加载态、禁用态和原生按钮语义。

### 实现流程

1. 在 `types.ts` 中定义 `type`、`size`、`nativeType` 等 props 的可选值。
2. 在 `Button.vue` 中通过 `defineProps(buttonProps)` 接收配置。
3. 用 `computedClass` 把 `type`、`size`、`round`、`circle`、`loading`、`plain`、`disabled` 这些输入转成 class。
4. 按 `loading` 和 `icon` 条件渲染内部图标。
5. 通过 `disabled || loading` 控制按钮是否真正不可点击。
6. 用 `defineExpose` 暴露原生按钮 ref，方便父组件命令式访问。

### 面试官会追问什么

- 为什么按钮需要保留 `nativeType`？
- 为什么 `loading` 要和 `disabled` 一起控制行为，而不只是切图标？
- 为什么这个组件要暴露按钮实例？
- 这个按钮为什么没有自己显式声明 `emits`？

### 回答方向

- `nativeType` 是为了兼容表单提交场景，组件库不能只做视觉层。
- `loading` 的本质是“防止重复操作”，所以必须影响行为，不只是 UI。
- 暴露实例是为了聚焦、测量、命令式控制等场景。
- 当前实现主要依赖根元素事件透传，后续如果对组件事件契约要求更严格，可以显式定义 `click` 事件。

### 代码层可优化点

- 如果后续要更严谨，可以显式 `defineEmits(['click'])`，对外事件契约会更清晰。
- 可以继续补 `aria-busy`、键盘态样式等无障碍能力。

## 3.2 ButtonGroup

### 组件职责

ButtonGroup 负责把多个按钮组织成一组，重点是组合关系而不是交互逻辑。

### 实现流程

1. 组件本身只渲染一个容器 `div.el-button-group`。
2. 所有按钮内容都由默认插槽传入。
3. 组内边框衔接、圆角合并和间距由样式控制，而不是由 JS 控制。

### 面试官会追问什么

- 为什么它这么简单还要单独抽组件？
- 它和 Button 各自的职责边界是什么？

### 回答方向

- 抽出来是为了统一样式语义和复用，不让页面层重复写组合样式。
- ButtonGroup 只负责“组”，Button 只负责“单个按钮行为”，不要相互侵入。

### 代码层可优化点

- 如果后续有更复杂的按钮组能力，比如分裂按钮、段选择器，可以在这个容器层继续演进。

## 3.3 Icon

### 组件职责

Icon 是第三方图标库的统一适配层，负责把 Font Awesome 的能力收口到组件库内部。

### 实现流程

1. 在 `main.ts` 和 VitePress 主题中统一注册图标库。
2. 在 `Icon.vue` 里引入 `FontAwesomeIcon`。
3. 用 `defineProps<IconProps>()` 接收对外参数。
4. 通过 `omit(props, ['color'])` 把 `color` 剥离出来，其他 props 继续透传到底层图标组件。
5. 用 CSS 变量 `--color` 管理颜色，保持样式层可控。

### 面试官会追问什么

- 为什么不直接在每个组件里使用 `FontAwesomeIcon`？
- 为什么要 `inheritAttrs: false`？
- 为什么颜色要自己处理，而不是直接交给底层图标组件？

### 回答方向

- 封装一层是为了隔离第三方依赖，避免业务和第三方库强耦合。
- `inheritAttrs: false` 是为了精确控制哪些属性落到包装层，哪些透传到底层。
- 自己处理颜色可以统一样式体系，也更方便后续主题化。

### 代码层可优化点

- 还可以继续补 `size`、旋转、动画等统一能力，不把所有特性都直接暴露到底层库。

## 3.4 Link

### 组件职责

Link 是对原生 `a` 标签的组件化封装，重点在语义不变、样式统一、行为可控。

### 实现流程

1. 在 `types.ts` 中定义 `type`、`underline`、`disabled`、`href`、`target`、`icon`。
2. 在 `Link.vue` 中基于 props 生成不同 class。
3. 如果链接被禁用，就让 `href` 置空、`target` 失效。
4. 点击时只在非禁用状态下触发 `click` 事件。
5. 可选渲染图标和 slot 内容。

### 面试官会追问什么

- 为什么 `disabled` 不是只改 class，而是还要改 `href`？
- Link 和 Button 的语义边界怎么分？

### 回答方向

- 因为 `a` 标签没有原生 `disabled`，只改样式不够，必须控制行为。
- Button 更偏动作触发，Link 更偏导航跳转，二者视觉可能接近，但语义不同。

### 代码层可优化点

- 可以增加 `rel="noopener noreferrer"` 等外链安全能力。

## 3.5 Alert

### 组件职责

Alert 用于页面内常驻提示，强调信息展示、主题区分、图标和关闭能力。

### 实现流程

1. 在 `types.ts` 中定义 `type`、`effect`、`closable`、`showIcon` 等配置。
2. 通过 `computed` 根据 props 生成 alert 的 class 集合。
3. 内部用 `visible` 控制是否展示。
4. 根据 `type` 计算对应图标名。
5. 点击关闭按钮时先隐藏组件，再触发 `close` 事件通知外部。
6. 用 `Transition` 包装，支持进出场动画。

### 面试官会追问什么

- Alert 和 Message 有什么本质区别？
- 为什么 Alert 适合做声明式组件？
- 为什么关闭动作要同时改内部状态和 `emit`？

### 回答方向

- Alert 是页面结构的一部分，适合长期展示；Message 是临时全局反馈。
- 声明式更适合页面内固定提示，不需要命令式创建和实例管理。
- 内部状态负责 UI，`emit` 负责把行为同步给外部，两者职责不同。

### 代码层可优化点

- 可以继续补标题和描述的更完整插槽能力。
- 可增加更细的无障碍属性，比如 `role="alert"`。

## 3.6 Rate

### 组件职责

Rate 是评分组件，核心是评分值状态、星星渲染和点击交互。

### 实现流程

1. 用 `RateProps` 定义 `nums`、`max`、`size`、`color`、`voidColor`。
2. 通过 `useRate` hook 初始化评分值 `rateNum`。
3. 模板里用 `v-for="num in max"` 渲染固定数量的星星。
4. 通过 `num <= rateNum` 判断是否高亮。
5. 点击某个星星时调用 `setRateNum(num)` 并触发变更事件。

### 面试官会追问什么

- 为什么要把评分逻辑拆成 hook？
- 为什么当前组件发的是 `changeRateNums`，你觉得这个 API 合理吗？

### 回答方向

- 拆 hook 是为了把“状态更新”和“UI 渲染”分离，哪怕逻辑简单，也是在练习可复用组织方式。
- 这个事件名能工作，但不够通用，后续更适合改成 `change` 或 `update:modelValue` 风格。

### 代码层可优化点

- 可以补 hover 预览、半星、只读态、键盘控制和无障碍属性。

## 3.7 Switch

### 组件职责

Switch 是布尔值或枚举值切换组件，重点在“值映射”而不是“样式切换”。

### 实现流程

1. 用 `SwitchProps` 定义 `modelValue`、`activeValue`、`inactiveValue`、颜色、文案和尺寸。
2. 内部维护 `switchOn`，通过比较 `modelValue === activeValue` 得到当前开关状态。
3. 监听外部 `modelValue` 变化，保持内部状态同步。
4. 点击时在 `activeValue` 和 `inactiveValue` 之间切换，并触发 `update:modelValue` 和 `change`。
5. 用 `computed` 根据状态计算开关背景色。
6. 根据 `inlinePrompt` 决定文字是在内部展示还是两侧展示。

### 面试官会追问什么

- 为什么要支持 `activeValue/inactiveValue`，而不只支持布尔值？
- `modelValue` 和内部 `switchOn` 为什么要分开维护？

### 回答方向

- 因为很多业务字段不是 `true/false`，可能是 `1/0`、`open/close`。
- 一个代表“业务值”，一个代表“当前 UI 是否打开”，职责不同，分开后更容易处理映射关系。

### 代码层可优化点

- 可以补 `beforeChange`、异步切换拦截和更完整的键盘可访问性。

## 3.8 DatePicker

### 组件职责

当前 DatePicker 更准确地说是一个轻量日历面板，负责月份切换、日历格生成和当天高亮。

### 实现流程

1. 把日历计算逻辑抽到 `calendar.ts`。
2. 通过 `generateCalendar(date)` 生成固定 42 格数据。
3. 在组件里用 `date` 维护当前面板日期。
4. 用 `computed` 生成 `calendarTable` 和顶部标题 `dateText`。
5. 通过 `changeMonth('prev' | 'next')` 切换显示月份。
6. 通过 `isActive(item)` 判断当天高亮状态。
7. 点击“今天”按钮时把面板回到当前日期。

### 面试官会追问什么

- 为什么日历表格通常固定做成 42 格？
- 你为什么把日期计算抽到单独文件？
- 这个组件现在更像 DatePicker 还是 Calendar？

### 回答方向

- 固定 42 格是为了让布局稳定，不会因为月份天数不同导致高度跳动。
- 日期逻辑天然适合抽离，组件层只保留状态和渲染。
- 当前更接近 Calendar 面板，真正成熟的 DatePicker 还会包含输入框、选中值输出、面板开合等能力。

### 代码层可优化点

- 当前闰年判断和“今天”判断值得继续校验优化。
- 还可以补日期选中、格式化输出、范围选择、键盘导航。

---

## 4. 组合与布局组件

## 4.1 Container

### 组件职责

Container 是布局容器，负责统一横向/纵向布局规则。

### 实现流程

1. 通过 `defineProps<ContainerProps>()` 接收 `direction`。
2. 用 `useSlots()` 读取默认插槽内容。
3. 如果显式传了 `direction`，优先使用。
4. 如果没传，就去分析插槽中是否有 `ElHeader` 或 `ElFooter`。
5. 如果存在头部或底部组件，就自动推断为纵向布局，否则默认为横向。
6. 最终输出 `el-container-horizontal` 或 `el-container-vertical` 类名。

### 面试官会追问什么

- 为什么要做自动方向推断？
- 为什么通过子组件 `name` 来判断，而不是通过 class？
- 这种设计的利弊是什么？

### 回答方向

- 自动推断是为了降低使用成本，像成熟组件库一样给出合理默认行为。
- 通过组件 `name` 判断更贴近组件语义，而不是依赖 DOM 结构细节。
- 好处是易用，风险是对组件命名有依赖，后续可以继续增强鲁棒性。

### 代码层可优化点

- 如果后续复杂度更高，可以引入更明确的布局上下文，而不是只看组件名。

## 4.2 Header / Footer / Main / Aside

### 组件职责

这四个组件负责组成语义化布局块。

### 实现流程

#### Header / Footer

1. 接收 `height` props。
2. 通过 `computed` 计算内联样式，高度默认 60px。
3. 渲染语义化标签 `<header>` / `<footer>`。

#### Aside

1. 接收 `width` props。
2. 用 `computed` 计算宽度，默认 200px。
3. 渲染 `<aside>`。

#### Main

1. 不接复杂 props。
2. 只负责渲染 `<main>` 并承载内容。

### 面试官会追问什么

- 为什么这些看起来很简单的块还要做成组件？
- 为什么 Header/Footer/Aside 用的是语义化标签？

### 回答方向

- 因为布局语义和默认尺寸可以被复用，外部页面不需要重复写。
- 语义化标签有利于结构清晰，也更符合组件库设计习惯。

### 代码层可优化点

- 后续可以支持响应式布局、折叠侧边栏、布局主题等扩展。

---

## 5. 父子联动组件

## 5.1 Collapse / CollapseItem

### 组件职责

Collapse 负责统一维护展开项状态，CollapseItem 负责单个面板的渲染和触发。

### 实现流程

#### Collapse

1. 接收 `modelValue` 和 `accordion`。
2. 内部维护 `activeNames`，并用 `watch` 同步外部值。
3. 定义 `setActiveNames`，统一负责更新内部值并触发 `update:modelValue` / `change`。
4. 定义 `handleItemClick`，根据是否是手风琴模式决定展开逻辑。
5. 通过 `provide` 把 `activeNames` 和 `handleItemClick` 传给子项。

#### CollapseItem

1. 接收 `name`、`title`、`disabled`。
2. 用 `inject` 获取父组件上下文。
3. 用 `computed` 判断自己当前是否激活。
4. 点击标题时，如果未禁用，就调用父组件的 `handleItemClick(name)`。
5. 通过 `v-show` 控制内容区展示。

### 面试官会追问什么

- 为什么这里适合用 `provide/inject`？
- 为什么 Collapse 自己不直接操作子组件 DOM，而是提供上下文？
- 手风琴模式和普通模式为什么要共用一套组件？

### 回答方向

- 因为这是非常典型的祖先统一管理、后代消费状态的场景。
- 组件化里应优先共享状态和行为，不直接操作子组件 DOM。
- 因为两者本质上是同一类折叠面板，只是激活项规则不同。

### 代码层可优化点

- 可以继续补键盘可访问性和动画高度过渡。
- 当前 `modelValue` 初始值依赖 watch 同步，后续也可以在初始化时更显式处理。

---

## 6. 浮层与弹出层体系

## 6.1 Tooltip

### 组件职责

Tooltip 是整个项目里最核心的底层浮层组件，负责触发方式、显示隐藏、点击外部关闭和 Popper 定位。

### 实现流程

1. 接收 `content`、`trigger`、`placement`、`manual`、`openDelay`、`closeDelay`、`popperOptions`。
2. 维护 `isOpen`、`triggerNode`、`popperNode`、`popperContainerNode`。
3. 根据 `trigger` 动态绑定事件：
   - `hover` 绑定 `mouseenter/mouseleave`
   - `click` 绑定点击切换
   - `manual` 时不绑定自动触发事件
4. 用 `debounce` 包装 `open/close`，支持延迟显示和延迟关闭。
5. 使用 `useClickOutside` 监听外部点击，在 click 模式下关闭弹层。
6. 监听 `isOpen`，当弹层打开且 DOM 已经渲染完成时，调用 `createPopper` 创建定位实例。
7. 组件卸载时销毁 Popper 实例。
8. 通过 `defineExpose` 暴露 `show/hide` 方法，给 Dropdown 和 Select 复用。

### 面试官会追问什么

- 为什么 Tooltip 要做成底层组件，而不是让 Dropdown / Select 各自实现？
- 为什么这里要用 Popper，而不是自己算位置？
- 为什么要支持 `manual` 模式？
- 为什么 `watch(isOpen)` 要用 `{ flush: 'post' }`？
- `openDelay/closeDelay` 这种逻辑为什么适合用 `debounce`？

### 回答方向

- Tooltip 是“浮层基础设施”，应该尽可能沉到能力层，不让业务组件重复写。
- 定位本身是复杂问题，工程上更适合依赖成熟库。
- `manual` 模式是为了让更复杂的业务组件命令式控制弹层。
- `flush: 'post'` 是为了保证 DOM 更新后再拿节点创建 Popper。
- `debounce` 天然适合处理 hover/click 延迟显示和关闭的问题。

### 代码层可优化点

- 当前事件对象 `events / outerEvents / dropdownEvents` 的重建方式还可以更稳健。
- 如果 props 中的 delay 动态变化，当前 debounce 实例不会自动重建，后续可继续优化。
- 可以继续补 `focus` 触发模式和更完整的无障碍支持。

## 6.2 Dropdown

### 组件职责

Dropdown 是对 Tooltip 的业务封装，负责菜单内容渲染、选择事件和点击后关闭策略。

### 实现流程

1. 外层直接复用 `Tooltip`。
2. 默认插槽作为触发器，`content` 插槽作为菜单内容。
3. 接收 `menuOptions` 后，用 `v-for` 渲染菜单项。
4. 菜单项支持 `disabled`、`divided`、自定义 label。
5. 点击菜单项时：
   - 如果禁用则直接返回
   - 触发 `select`
   - 如果 `hideAfterClick` 为真，则调用 tooltip 实例的 `hide()`
6. 通过 `defineExpose` 把 `show/hide` 再继续暴露出去。

### 面试官会追问什么

- 为什么 Dropdown 不自己管定位？
- `RenderVnode` 在这里的作用是什么？
- 为什么这里要通过 ref 调 Tooltip 的 `hide()`？

### 回答方向

- Dropdown 的重点是菜单行为，不是浮层基础能力。
- `RenderVnode` 是为了兼容 label 既可能是字符串，也可能是 VNode。
- 因为 Dropdown 处于 Tooltip 之上，需要命令式关闭弹层。

### 代码层可优化点

- 可以继续补键盘导航、选中态、嵌套菜单和更完整的角色属性。

## 6.3 Dialog

### 组件职责

Dialog 是一个通用模态框，重点在显示生命周期、关闭策略、拖拽和滚动管理。

### 实现流程

1. 接收 `modelValue`、`title`、`width`、`top`、`modal`、`showClose`、`destroyOnClose`、`draggable`、`beforeClose` 等配置。
2. 用 `visible` 控制当前展示，用 `rendered` 控制 DOM 是否保留。
3. 监听外部 `modelValue`：
   - 打开时设置 `rendered = true`、`visible = true`
   - 关闭时先让 `visible = false`
4. 打开时触发 `open` 事件并根据配置锁定 body 滚动。
5. 关闭时支持 3 种入口：
   - 关闭按钮
   - 点击遮罩
   - 按 ESC
6. 如果配置了 `beforeClose`，就把真正关闭逻辑包装成 `done` 传给外部。
7. 拖拽时在 header 的 `mousedown` 记录起点，在全局 `mousemove` 更新位移。
8. 离场动画结束后恢复滚动，并在 `destroyOnClose` 为真时销毁 DOM。

### 面试官会追问什么

- 为什么要把 `visible` 和 `rendered` 拆开？
- 为什么 `beforeClose` 要用回调而不是简单返回布尔值？
- 为什么拖拽是通过 `transform` 实现，而不是直接改 `top/left`？
- 锁滚动为什么要保存旧的 `bodyOverflow`？

### 回答方向

- 一个控制显示，一个控制销毁，拆开后动画和卸载互不影响。
- 回调方式更适合兼容异步确认逻辑。
- `transform` 对位移场景更自然，也不容易破坏初始布局。
- 保存旧值是为了关闭后准确恢复，而不是粗暴写死。

### 代码层可优化点

- 可以继续补焦点陷阱、首个可聚焦元素定位、Tab 键循环等无障碍能力。
- 还可以补 Teleport，把弹窗统一挂到 body。

## 6.4 Message

### 组件职责

Message 是函数式全局消息组件，重点在动态创建、堆叠、自动关闭和销毁。

### 实现流程

#### 组件层 `Message.vue`

1. 接收 `id`、`message`、`duration`、`showClose`、`type`、`zIndex`、`offset`、`onClose`。
2. 挂载后自动显示并启动关闭定时器。
3. 根据前一个消息实例的底部位置计算自己的 top。
4. 鼠标移入时清除定时器，移出时重新计时。
5. 点击关闭或倒计时结束时，把 `visible` 设为 `false`。
6. 离场动画结束后执行 `onClose`，交给控制层真正销毁。

#### 控制层 `method.ts`

1. 统一把字符串、VNode 和对象参数归一化。
2. 通过 `h(MessageConstructor, messageProps)` 创建 vnode。
3. 通过 `render(vnode, container)` 动态挂载。
4. 把实例信息放入 `instances` 数组。
5. 通过 `getLastBottomOffset` 计算新消息堆叠位置。
6. 关闭时先让组件 `visible=false`，等动画结束再销毁实例。

### 面试官会追问什么

- 为什么 Message 不适合做声明式组件？
- 为什么 Message 需要实例池？
- 为什么销毁不是立即 `render(null)`，而是等动画结束？
- 为什么要单独抽 `useZIndex`？

### 回答方向

- 因为 Message 更像随时调用的全局反馈，不适合业务模板里预先写死。
- 实例池是为了做堆叠、关闭指定实例和 closeAll。
- 因为立即销毁会让离场动画消失。
- z-index 是跨多个动态浮层的通用问题，值得抽离。

### 代码层可优化点

- 可以继续补最大消息数、同内容合并、防抖触发等能力。
- 当前容器挂载策略还可以继续封装得更统一。

## 6.5 MessageBox

### 组件职责

MessageBox 是 Promise 风格的函数式确认框，适合“确认/取消/关闭”这种明确流程。

### 实现流程

#### 展示层 `MessageBox.vue`

1. 接收 `title`、`content`、`showCancelBtn` 等参数。
2. 内部维护 `state.visible` 和 `state.type`。
3. 点击确认、取消或关闭时，记录操作类型并关闭弹层。
4. 通过 `defineExpose` 把 `setVisible` 和 `state` 暴露给控制层。

#### 控制层 `MessageBox.ts`

1. 对外暴露 `MessageBox()`、`MessageBox.confirm()`、`MessageBox.alert()`。
2. 使用 `createApp(MessageBoxComponent, options)` 动态创建实例。
3. 挂载后调用 `vm.setVisible(true)` 展示弹窗。
4. 通过 `watch(vm.state)` 监听是否关闭。
5. 一旦关闭，就把 `confirm/cancel/close` 作为 Promise 结果 `resolve` 给调用方。
6. 结束后 `app.unmount()` 卸载实例。

### 面试官会追问什么

- 为什么 MessageBox 适合返回 Promise？
- 为什么这里用 `createApp` 而不是 `h + render`？
- MessageBox 和 Dialog 的职责边界怎么区分？

### 回答方向

- Promise 最适合表达“等待用户做决定”的流程。
- MessageBox 更像一次独立的组件实例化，而不是单纯插一个 vnode。
- Dialog 是通用容器，MessageBox 是带预设交互流程的确认弹窗。

### 代码层可优化点

- 可以继续补输入型 MessageBox、异步确认态、按钮 loading 和关闭前校验。
- 更稳妥的挂载方式也可以考虑先挂到独立 div 容器上。

---

## 7. 输入与表单体系

## 7.1 Input

### 组件职责

Input 是整个输入体系的基础，除了文本输入，还承担插槽扩展、密码切换、清空和表单校验联动。

### 实现流程

1. 通过 `InputProps` 定义 `modelValue`、`type`、`disabled`、`showClear`、`showPassword`、`placeholder`、`size` 等配置。
2. 内部维护 `inputValue`，并用 `watch(props.modelValue)` 同步外部值。
3. 输入时更新 `inputValue`，触发 `update:modelValue` 和 `input`。
4. 改变时触发 `change`。
5. 聚焦/失焦时触发对应事件，并更新 focus 状态。
6. 如果开启 `showClear`，则根据是否有输入内容决定是否显示清空图标。
7. 如果开启 `showPassword`，则在 `password/text` 之间切换输入类型。
8. 通过 `inject(formItemContextKey)` 获取当前表单项上下文，在 input/change/blur 时机触发校验。
9. 通过具名插槽支持 `prefix`、`suffix`、`prepend`、`append`。

### 面试官会追问什么

- 为什么要维护 `inputValue`，而不是直接全靠 props？
- 为什么 Input 要去感知 FormItem 上下文？
- 清空和密码切换为什么也适合内聚在 Input 里？
- 你觉得这个组件最容易出错的地方是什么？

### 回答方向

- 因为输入过程本身就是局部状态，内部维护更自然，同时再和外部同步。
- 因为表单联动是输入组件的重要增强能力，但又不应该强耦合到 Form 本体。
- 因为它们都属于“输入行为增强”，放在 Input 里更统一。
- 最容易出错的是外部值与内部值同步、清空逻辑、以及和表单触发时机的协同。

### 代码层可优化点

- 当前 `clear` 事件类型定义了但清空逻辑里没有真正发出，后续应补齐。
- `computedClass` 中 focus class 依赖的写法还可以更严谨。
- 可以继续补 textarea、多行输入、字数统计、组合输入等能力。

## 7.2 Select

### 组件职责

Select 负责在输入框与下拉面板之间建立选择关系，是一个“输入 + 浮层 + 选项状态 + 过滤逻辑”的复合组件。

### 实现流程

1. 接收 `modelValue`、`options`、`clearable`、`filterable`、`filterMethod`、`remote`、`remoteMethod`、`renderLabel` 等配置。
2. 初始化时根据 `modelValue` 找到对应 option，拆成：
   - `states.inputValue`
   - `states.selectOption`
   - `states.mouseHover`
   - `states.loading`
3. 通过 `ElTooltip` 的 `manual` 模式承载下拉面板。
4. 通过自定义 Popper modifier 保证面板和输入框同宽。
5. 点击外层区域时切换下拉打开/关闭。
6. 如果开启过滤：
   - 优先走 `filterMethod`
   - 否则在 `remote + remoteMethod` 下走异步搜索
   - 再不行就用默认 `label.includes`
7. 为远程搜索配合 `debounce`，减少请求频率。
8. 点击某个 option 后：
   - 更新 `selectOption`
   - 更新输入框显示文本
   - 触发 `change` 和 `update:modelValue`
   - 关闭面板
9. 如果开启清空且鼠标悬浮、当前有值，就展示清空图标。
10. 点击清空后重置状态并触发 `clear`、`change`、`update:modelValue`。

### 面试官会追问什么

- 为什么 `inputValue` 和 `selectOption` 要拆开？
- 为什么 Select 要复用 Tooltip，而不是自己做下拉层？
- 为什么过滤逻辑要统一收口，而不是散在事件回调里？
- 远程搜索为什么要做防抖？
- 当前实现如果做多选会遇到什么问题？

### 回答方向

- 一个是“显示态”，一个是“选中态”，拆开后交互更稳定。
- Tooltip 已经解决了浮层定位和关闭能力，Select 应该专注在选择行为。
- 收口到统一函数里更容易维护优先级和扩展策略。
- 防抖是为了减少无意义请求，提升体验和性能。
- 多选会把单值状态模型全部改掉，包括输入框展示、选项状态、清空逻辑和事件类型。

### 代码层可优化点

- 可以补多选、虚拟滚动、键盘导航、远程请求取消。
- 当前 debounce 时间初始化后不随 props 变化动态更新，后续可继续增强。

## 7.3 Form

### 组件职责

Form 是表单控制中心，负责字段注册、整表校验、重置和清空校验状态。

### 实现流程

1. 接收 `model` 和 `rules`。
2. 内部维护 `fields` 数组，存放所有注册的 `FormItemContext`。
3. 提供 `addField/removeField` 给 FormItem 注册和注销。
4. 提供 `resetFields`，统一调度字段恢复初始值。
5. 提供 `clearValidate`，统一清空字段的错误状态。
6. 提供 `validate`，遍历所有字段并收集校验结果，最终返回 `true` 或 reject。
7. 通过 `provide(formContextKey, ...)` 把这些能力下发给 FormItem。
8. 用 `defineExpose` 把 `validate`、`resetFields`、`clearValidate` 暴露给外部页面。

### 面试官会追问什么

- 为什么 Form 要维护字段注册表？
- 为什么 `validate` 不直接在父组件里对 `model` 全量跑，而是要依赖每个 FormItem？
- 为什么这里要把能力 `expose` 给外部？

### 回答方向

- 因为表单真正可被操作的是“字段实例”，不是一个纯数据对象。
- 每个 FormItem 负责自己的规则、状态和错误信息，Form 只做调度更合理。
- 因为业务页面需要命令式触发整表校验和重置。

### 代码层可优化点

- 后续可以继续补滚动到错误项、局部字段校验、异步校验状态统一管理。

## 7.4 FormItem

### 组件职责

FormItem 负责单字段的取值、规则匹配、错误展示和字段级能力暴露。

### 实现流程

1. 接收 `label`、`prop`、`showMessage`。
2. 通过 `inject(formContextKey)` 获取表单上下文。
3. 用 `computed` 根据 `prop` 从 `formContext.model` 中取当前字段值。
4. 用 `computed` 根据 `prop` 从 `formContext.rules` 中取当前字段规则。
5. 在挂载时记录 `initialValue`，并把自己注册到 Form。
6. 根据触发类型过滤当前应该执行的规则。
7. 调用 `async-validator` 执行校验，并维护 `validateStatus`：
   - `state`
   - `errorMsg`
   - `loading`
8. 提供 `clearValidate` 和 `resetField`。
9. 再通过 `provide(formItemContextKey, context)` 把字段级校验能力传给 Input。
10. 组件卸载时把自己从 Form 移除。

### 面试官会追问什么

- 为什么 FormItem 既要消费 Form 上下文，又要再提供一层上下文给 Input？
- 为什么要保存 `initialValue`？
- 为什么规则要按 trigger 过滤？

### 回答方向

- 因为它处在表单系统的中间层，上接表单调度，下接输入控件。
- 因为 reset 本质上是恢复初始状态。
- 因为不同规则应该在不同用户交互时机触发，而不是每次全跑。

### 代码层可优化点

- 后续可以支持更丰富的错误展示位置、label 宽度控制和多类型控件适配。

---


## 8. 渲染辅助组件

## 8.1 RenderVnode

### 组件职责

RenderVnode 是内部工具组件，负责把字符串或 VNode 统一渲染出来，常用于 Dropdown、Select、Message 这类需要渲染动态内容的场景。

### 实现流程

1. 通过 `defineComponent` 定义一个极轻量组件。
2. 接收必须的 `vNode` props，类型是 `String | Object`。
3. 在 `setup` 中直接返回渲染函数 `() => props.vNode`。

### 面试官会追问什么

- 为什么不直接在模板里写 `{{ item.label }}`？
- 为什么这里要用 render function？
- 这种组件体现了你对 Vue 的什么理解？

### 回答方向

- 因为 label 不一定是纯文本，也可能是 VNode。
- render function 更适合做“把传入内容原样渲染”的能力组件。
- 它体现的是我知道 Vue 除了模板，还有基于 vnode 的更底层渲染方式。

### 代码层可优化点

- 如果后续内容类型更多，可以继续补更严格的类型约束。

---

## 9. 作为面试官，我会重点深挖哪些组件

如果我是前端面试官，看完这个项目，我最想深挖的不是全部组件，而是下面 6 个：

1. `Form / FormItem / Input`
原因：最能体现组件通信、字段注册和校验抽象能力。

2. `Tooltip`
原因：最能体现基础能力抽象、事件建模和第三方库整合。

3. `Select`
原因：最能体现复合组件状态设计和交互完整性。

4. `Dialog`
原因：最能体现生命周期、关闭策略和交互增强。

5. `Message / MessageBox`
原因：最能体现命令式渲染和函数式组件封装。

6. `DatePicker`
原因：最能看出你会不会把 UI 问题拆成纯算法逻辑和渲染逻辑。

你在真正面试里，也建议优先主动把这几个讲出来。

## 10. 作为面试官，我最喜欢追的发散题

这些问题你最好提前准备，不然很容易在“组件都讲明白了”之后被卡住。

### 发散题 1

为什么这个项目里很多复杂组件都不是直接用全局状态管理，而是优先用局部状态和 `provide/inject`？

### 发散题 2

为什么你把 Tooltip 做成基础层，而不是把 Dropdown 做成基础层？

### 发散题 3

为什么 Message 用 `h + render`，MessageBox 用 `createApp`？

### 发散题 4

为什么组件库项目里，类型声明输出和样式入口暴露也算核心能力，而不只是“附加功能”？

### 发散题 5

如果让你把这个项目继续做成一个更成熟的组件库，你最先补哪三件事？

推荐回答思路：

- 第一步补可访问性和键盘交互。
- 第二步补按需加载、CI 和发布流程。
- 第三步补复杂组件的更完整能力，比如 Select 多选、DatePicker 真正选值、Dialog Teleport。

## 11. 最后一轮复习建议

面试前请至少把下面这些源码再过一遍：

- `src/components/Tooltip/Tooltip.vue`
- `src/components/Select/Select.vue`
- `src/components/Form/Form.vue`
- `src/components/Form/FormItem.vue`
- `src/components/Input/Input.vue`
- `src/components/Dialog/Dialog.vue`
- `src/components/Message/method.ts`
- `src/components/MessageBox/MessageBox.ts`
- `src/components/DatePicker/calendar.ts`
- `src/components/Common/RenderVnode.ts`

如果你能把这 10 个文件顺着讲清楚，已经足够接住这个项目 80% 以上的代码级追问。

---

## 12. 作为面试官，离开组件源码后我还会继续深挖什么

如果我是面试官，我不会只停在“组件会不会写”，我通常会继续追到下面这些技术层问题。

## 12.1 Vue 3

我会追问：

- 为什么这个项目大量使用组合式 API，而不是 Options API？
- `computed` 和 `watch` 你在这个项目里怎么区分使用场景？
- 为什么 Form 和 Collapse 用 `provide/inject`，不用层层 props？
- `defineExpose` 在这个项目里解决了什么问题？
- `h`、`render`、`createApp` 这三个 API 分别用在了哪里，为什么？

你要答的重点：

- 组合式 API 更适合抽离组件库逻辑。
- `computed` 负责派生值，`watch` 负责副作用。
- `provide/inject` 适合祖先统一调度、后代消费上下文的场景。
- `defineExpose` 是命令式能力开放。
- `h/render/createApp` 体现的是你对 Vue 命令式渲染能力的理解。

## 12.2 Vite

我会追问：

- 为什么组件库项目选 Vite？
- 库模式是怎么配的？
- 为什么要把 Vue 设成 external？
- `module`、`main`、`types`、`exports` 这些字段分别有什么作用？

你要答的重点：

- Vite 兼顾开发效率和库模式构建。
- `vite.config.ts` 里通过 `mode === 'lib'` 切到库模式。
- Vue external 是为了避免重复打包和宿主冲突。
- 这些字段共同决定了 npm 包如何被消费。

## 12.3 TypeScript

我会追问：

- TypeScript 在这个项目里最真实的价值是什么？
- 为什么有的地方用 `interface`，有的地方用 `PropType`？
- `InjectionKey` 为什么重要？
- 你输出类型声明的意义是什么？

你要答的重点：

- TS 不只是提示，而是约束组件 API 和上下文对象。
- `PropType` 偏运行时声明，`interface + defineProps<T>` 偏类型层描述。
- `InjectionKey` 是为了让 `provide/inject` 也保持类型安全。
- 类型声明输出是组件库交付的一部分。

## 12.4 Pinia

我会追问：

- 这个项目为什么没用 Pinia？
- 如果后续接入，你会把它用在哪？
- Pinia 和 Vuex 最大差异是什么？
- 什么时候你不会上 Pinia？

你要答的重点：

- 一定先说清楚：当前项目是组件库，没有真实接入 Pinia。
- 当前主要是局部状态和上下文通信，不需要全局状态管理。
- 如果后续文档站需要全局主题、AI 历史会话、用户偏好或跨页面状态，再考虑引入。
- 只有跨页面、跨模块、共享复杂状态时，Pinia 才值得引入。

## 12.5 测试

我会追问：

- 为什么用 Vitest？
- 你到底测了什么，不要泛泛说“做了单测”。
- 为什么要 mock Popper 和 ResizeObserver？
- 组件测试和业务页面测试思路有什么不同？

你要答的重点：

- Vitest 和 Vite 体系一致，开发体验更好。
- 当前测试覆盖基础组件、交互组件和表单联动。
- mock 是为了稳定测试边界，聚焦业务逻辑而不是浏览器环境差异。
- 组件测试更强调 API、交互和边界行为，不是只测页面文案。

## 12.6 RAG / Node 服务

我会追问：

- 你这个 AI 助手不是简单调接口，那完整链路是什么？
- 为什么知识源不只用 markdown？
- 为什么要结合 route 和组件名做检索增强？
- 当前实现最大的工程化短板是什么？

你要答的重点：

- 链路要讲清楚：前端提问 -> 服务端切片 -> embedding -> Qdrant 检索 -> LLM 生成。
- 文档、demo、types 三类知识源共同提高回答准确性。
- 路由和组件名是为了做更精确召回。
- 当前仍有缓存、增量索引、并发控制等可优化空间。

## 12.7 你回答时最好的过渡方式

如果面试官刚问完组件源码，你可以这样自然过渡到技术层：

> 这个组件本身我讲完了，如果再往下拆，其实它背后主要考的是 Vue 组件通信、状态设计和工程化组织。  
> 比如这里我用到了 `provide/inject`、`watch`、命令式渲染，继续深挖的话，我也可以从 Vue3、Vite 打包或者组件库类型输出这几个角度展开。

这句话很好用，因为它会把谈话主动权拉回到你熟悉的方向上。
