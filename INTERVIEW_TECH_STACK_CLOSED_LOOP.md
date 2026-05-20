# TinyElement 技术栈与面试闭环文档

这份文档基于当前仓库代码整理，目标不是背题，而是把项目讲成一个完整的面试故事：技术栈是什么，为什么这样选，在项目里怎么落地，面试官会怎么追问，以及你如何从组件实现一路讲到工程化、性能优化、浏览器原理和底层机制。

## 1. 项目一句话

TinyElement 是一个仿 Element Plus 思路实现的 Vue 3 + TypeScript 组件库，包含基础组件、表单组件、浮层组件、反馈组件、VitePress 文档站、Vitest 单元测试，以及一个接入文档上下文的 AI 问答助手服务。

面试开场可以这样说：

> 我做的是一个 Vue 3 + TypeScript 组件库项目，重点不只是写 UI，而是按组件库的方式设计公共 API、类型约束、全局安装、按需导出、样式 token、文档示例、测试和库模式构建。项目里比较有代表性的部分是 Form 的上下文通信和 async-validator 校验、Tooltip/Select 的弹层定位、Message/MessageBox 的命令式挂载，以及 VitePress 文档站和 AI 助手的工程整合。

## 2. 技术栈总览

| 分类 | 技术栈 | 项目落点 | 面试价值 |
| --- | --- | --- | --- |
| 核心框架 | Vue 3.3、SFC、Composition API、`<script setup>` | `src/components/**/*.vue` | 讲响应式、组件通信、生命周期、宏编译、v-model |
| 类型系统 | TypeScript 5、`PropType`、`ExtractPropTypes`、`InjectionKey` | `types.ts`、`Form/types.ts` | 讲公共 API 类型设计、泛型、声明文件 |
| 构建工具 | Vite 5、Rollup library mode、`@vitejs/plugin-vue` | `vite.config.ts` | 讲库构建、external、产物格式、开发体验 |
| 包发布 | `main`、`module`、`types`、`exports`、`peerDependencies` | `package.json` | 讲 npm 包设计、ESM/UMD、类型入口、样式入口 |
| 文档站 | VitePress、`@vitepress-demo-preview` | `docs/`、`docs/.vitepress/config.ts` | 讲组件库文档、demo 预览、主题增强 |
| 路由演示 | Vue Router 4、hash history、动态 import | `src/router/index.ts` | 讲 demo 系统、路由懒加载、hash/history 区别 |
| 测试 | Vitest、Vue Test Utils、jsdom、mock | `vitest.config.ts`、`*.test.ts` | 讲组件测试、交互测试、定时器和第三方库 mock |
| 表单校验 | async-validator | `FormItem.vue` | 讲 schema 校验、触发时机、异步校验 |
| 浮层定位 | Popper.js | `Tooltip.vue`、`Select.vue` | 讲定位、滚动容器、z-index、Teleport、重排 |
| 工具函数 | lodash-es、debounce、isNil、isFunction | `Input`、`Select`、`FormItem` | 讲防抖、工具函数、ESM tree shaking |
| 图标 | Font Awesome | `Icon.vue`、`main.ts`、VitePress theme | 讲图标封装、统一 API、全局图标库 |
| 样式系统 | CSS Variables、全局样式入口、SCSS、PostCSS nested | `src/styles/`、组件 `style.css` | 讲设计 token、主题化、样式隔离、sideEffects |
| Node 服务 | Express、SSE、OpenAI-compatible API、Qwen | `server/src/app.ts` | 讲服务端代理、API key 安全、流式响应 |
| AI 文档助手 | MarkdownIt、highlight.js、ResizeObserver、localStorage、虚拟列表 | `AiAssistant.vue` | 讲前端流式渲染、上下文采集、长列表性能 |
| 预留 RAG | Embeddings、Qdrant、检索重排 | `server/src/services/*` | 讲 RAG 架构，但要说明当前主服务未完整接入 |

### 2.1 技术栈面试价值详细回答

这部分可以直接作为“面试价值”列的展开话术。回答时不要只说“我用了某某技术”，而要按“解决的问题 -> 项目落点 -> 设计取舍 -> 可优化点”展开。

#### 2.1.1 核心框架：Vue 3、SFC、Composition API、`<script setup>`

**面试回答：**

> 在 TinyElement 里，Vue 3 不只是渲染 UI 的框架，它支撑的是组件库的公共 API、响应式状态、组合组件通信和生命周期副作用管理。组件库组件通常不是单一页面逻辑，而是多个能力的组合，比如 Input 同时要处理 `v-model`、清空、密码显隐、插槽、表单校验联动；Dialog 要处理显示状态、遮罩、滚动锁定、拖拽和 ESC 关闭。Composition API 可以让我按能力组织代码，把状态、计算属性、监听、副作用和对外暴露的方法拆清楚。`<script setup>` 则减少样板代码，`defineProps`、`defineEmits`、`defineExpose` 这些宏在编译阶段处理，更适合组件库里大量 SFC 的书写。

**可以主动补充：**Vue 3 的响应式底层基于 Proxy、effect、track/trigger。`computed` 适合做可缓存的派生状态，比如 Button 类名；`watch` 适合处理副作用，比如同步 `modelValue`、打开 Tooltip 后创建 Popper。Composition API 的边界是不能把所有逻辑堆在 `setup` 里，跨组件复用的 DOM 副作用应该继续抽成 hook。

#### 2.1.2 类型系统：TypeScript、`PropType`、`ExtractPropTypes`、`InjectionKey`

**面试回答：**

> TypeScript 在组件库里的核心价值不是给内部变量简单标类型，而是把对外 API 变成稳定契约。使用者真正依赖的是 props、emits、slots、expose 方法、上下文协议和声明文件。比如 Button 的 `type`、`size` 可以用联合类型限制；Form 的上下文用 `InjectionKey<FormContext>`，让 FormItem 注入后仍然有类型提示；Tooltip 的 placement 可以复用 Popper 类型，避免重复维护一份字符串枚举。这样既减少使用者传错值，也让后续维护组件 API 时更可控。

**可以主动补充：**`PropType<T>` 解决的是 Vue 运行时 props 声明和 TS 静态类型之间的桥接；`ExtractPropTypes` 可以从 props 配置反推出内部类型，减少重复声明；`.d.ts` 则是组件库发布给外部项目的类型合同。面试里要强调“公共 API 类型设计”，不要只停在“我用了 TypeScript”。

#### 2.1.3 构建工具：Vite、Rollup library mode、`@vitejs/plugin-vue`

**面试回答：**

> Vite 在项目里承担两类职责：开发阶段提供快速冷启动和热更新，发布阶段通过 Rollup library mode 产出组件库包。组件库和普通业务项目的构建目标不同，业务项目最终是一个应用，而组件库最终要被其他项目安装，所以要关注产物格式、外部依赖、类型声明和 tree-shaking。项目里 library mode 输出 ES/UMD，并把 Vue 配置为 external，避免把 Vue 运行时打进库包。

**可以主动补充：**把 Vue external 掉的原因是宿主项目本身就会安装 Vue，如果组件库内置一份 Vue，可能造成包体变大、重复运行时甚至响应式上下文不一致。ESM 产物利于 tree-shaking，UMD 产物更偏浏览器直接引入或兼容场景。真正完善时还要拆分组件入口和样式入口。

#### 2.1.4 包发布：`main`、`module`、`types`、`exports`、`peerDependencies`

**面试回答：**

> 组件库的 `package.json` 不是简单写依赖，它决定了使用者如何消费这个包。`main`、`module`、`types` 分别服务于不同的模块系统和 TypeScript 类型入口；`exports` 用来声明稳定的可访问路径，避免使用者依赖内部不稳定文件；`peerDependencies` 用来表达“组件库需要宿主项目提供 Vue”。这些配置共同决定了全量引入、按需引入、类型提示和构建兼容性。

**可以主动补充：**`dependencies` 会随库一起安装，`peerDependencies` 更像版本约束和宿主协作协议。Vue 这类运行时框架通常应该放在 peerDependencies。样式文件属于副作用资源，如果做 tree-shaking，还需要在 `sideEffects` 中正确保留 CSS。

#### 2.1.5 文档站：VitePress、demo preview、主题增强

**面试回答：**

> 组件库的交付物不只是源码，还包括文档体验。VitePress 在 TinyElement 里承担组件说明、API 表格、demo 预览和使用示例的职责。这样使用者不用读源码就能知道组件怎么用，维护者也能通过 demo 快速验证交互行为。项目里的文档站通过 demo preview 把 Markdown 和 Vue 示例连接起来，并在主题层挂载 AI 助手，说明文档站也可以作为组件库的工程化入口。

**可以主动补充：**文档站构建和组件库构建目标不同。文档站是一个网站，重点是可读性和示例体验；组件库构建是 npm 包，重点是模块格式、类型声明和按需能力。面试里可以说“文档即产品”，但不要夸大成完整设计系统。

#### 2.1.6 路由演示：Vue Router、hash history、动态 import

**面试回答：**

> `src/router` 主要服务于本地开发演示，不属于组件库最终对外 API。它的价值是把不同组件的开发调试页面组织起来，便于在浏览器里快速验证 Button、Input、Form、Tooltip 等组件状态。动态 import 可以让不同 demo 页面按路由拆分，避免开发演示首屏一次性加载所有示例。

**可以主动补充：**hash history 的优点是本地部署简单，不依赖服务端路由回退；缺点是 URL 不够干净。这个点适合说明“开发调试系统”和“发布包”是分离的，组件库源码不应该依赖 demo 路由运行。

#### 2.1.7 测试：Vitest、Vue Test Utils、jsdom、mock

**面试回答：**

> 组件库测试重点不是测试页面截图，而是验证公共 API 稳定性：props 是否影响渲染，emits 是否按预期触发，插槽是否生效，命令式方法是否可用，表单校验是否 resolve/reject。Vitest 提供测试运行环境，Vue Test Utils 负责挂载组件和触发交互，jsdom 模拟基础浏览器 DOM。像 Popper 这种第三方定位库，不需要在单元测试里验证具体坐标，而是 mock 它，验证组件是否在正确时机创建和销毁定位实例。

**可以主动补充：**fake timers 适合测试 debounce、延迟关闭和动画等待；`afterEach` 清理 DOM 可以避免用例之间互相污染。后续可以加覆盖率门禁、Playwright E2E 和可访问性测试。

#### 2.1.8 表单校验：async-validator

**面试回答：**

> 表单校验如果只在 Input 内部做，会很难统一管理字段状态、重置和整体提交。TinyElement 把 Form、FormItem、Input 分层：Form 保存 model、rules 和字段注册表；FormItem 负责当前字段的 rules、trigger、校验状态；Input 只负责具体输入交互，并在 blur/change/input 时通知 FormItem。async-validator 的价值是把规则抽象成 schema，支持 required、pattern、自定义 validator 和异步 Promise。

**可以主动补充：**trigger 过滤能避免所有规则在每次输入时都执行。resetFields 通常需要记录初始值，否则无法恢复表单。异步校验要注意竞态，生产级可以给校验加序号或取消机制，只采纳最后一次结果。

#### 2.1.9 浮层定位：Popper.js

**面试回答：**

> Tooltip、Select、Dropdown 这类浮层组件的难点不只是显示隐藏，而是定位。真实场景要考虑触发元素尺寸、滚动容器、窗口边界、placement、offset、flip、箭头和 z-index。项目里用 Popper.js 负责复杂定位，Tooltip 只封装触发方式、显示状态、外部点击关闭和生命周期管理；Select 再复用 Tooltip 的 manual 模式作为下拉面板能力。

**可以主动补充：**生产级浮层通常会结合 Teleport 挂到 body，避免父容器 `overflow: hidden`、`transform` 和层叠上下文影响定位。代价是要补焦点管理、键盘操作、ARIA、滚动锁定和事件回收。

#### 2.1.10 工具函数：lodash-es、debounce、isNil、isFunction

**面试回答：**

> 工具函数在组件库里不是为了偷懒，而是为了让边界判断和高频交互更稳定。比如 Select 的远程搜索需要 debounce，避免用户每输入一个字符都触发请求；`isNil` 可以统一处理 `null/undefined`；`isFunction` 可以在调用用户传入的回调前做类型保护。选择 `lodash-es` 的原因是它基于 ESM，更利于构建工具做 tree-shaking。

**可以主动补充：**工具库也不能滥用。简单判断可以自己写，复杂且容易出错的能力才适合复用成熟工具。面试里可以把 debounce 延伸到竞态处理：防抖减少请求次数，但不能完全解决返回顺序问题，必要时还要加请求序号或 AbortController。

#### 2.1.11 图标：Font Awesome 与 Icon 封装

**面试回答：**

> 组件库不应该让业务方直接散落使用第三方图标 API，所以 TinyElement 封装了 Icon 组件，把图标、颜色、尺寸、旋转等能力收口成统一接口。这样 Button、Alert、Message 等组件都能使用同一套图标规范，也方便后续替换底层图标库。入口和文档站注册图标库，则保证 demo 和真实使用方式一致。

**可以主动补充：**封装第三方库的价值是隔离变化，而不是简单包一层。边界是要控制引入图标的数量，避免把整套图标都打进包里；更完善的方案可以支持按需注册、默认图标集和自定义图标。

#### 2.1.12 样式系统：CSS Variables、全局样式入口、SCSS、PostCSS nested

**面试回答：**

> 组件库样式系统要解决一致性、可覆盖和发布入口三个问题。TinyElement 把颜色、字号、边框、圆角、动画时长等抽成 CSS Variables，组件样式都消费这些 token，使用者可以通过覆盖变量实现主题调整。`src/styles/index.css` 作为统一样式入口，方便全量引入；每个组件保留自己的 style，则为后续按需样式入口打基础。

**可以主动补充：**CSS Variables 是运行时变量，适合主题切换；Sass 变量是编译期变量，适合预处理和结构化组织。组件库发布时 CSS 是副作用，tree-shaking 场景下要用 `sideEffects` 正确保留。当前项目更偏全量样式入口，生产级可继续补独立样式入口。

#### 2.1.13 Node 服务：Express、SSE、OpenAI-compatible API、Qwen

**面试回答：**

> AI 文档助手选择服务端代理，是因为 API key 不能暴露在浏览器里。前端只负责采集当前文档上下文、发送问题和渲染流式结果；Express 服务负责读取环境变量、拼接 prompt、调用兼容 OpenAI 协议的大模型接口，并用 SSE 把增量内容转发给前端。这样安全边界更清楚，也方便后续加限流、日志、上下文裁剪和错误处理。

**可以主动补充：**SSE 适合服务端向浏览器单向持续推送，比如大模型 token 流；WebSocket 更适合强双向实时通信。开发环境通过 VitePress proxy 转发 `/api/chat`，可以避免前端硬编码服务地址和跨域问题。

#### 2.1.14 AI 文档助手：MarkdownIt、highlight.js、ResizeObserver、localStorage、虚拟列表

**面试回答：**

> AI 助手前端的难点不是普通表单提交，而是流式渲染和长对话体验。浏览器端通过 fetch stream 读取 SSE chunk，逐步更新回答文本，再用 MarkdownIt 渲染 Markdown、highlight.js 高亮代码。消息列表如果无限增长，会造成 DOM 过多，所以项目用虚拟列表减少实际渲染节点；动态高度消息则通过 ResizeObserver 回填真实高度。localStorage 用于保留一定的会话状态，提升文档问答体验。

**可以主动补充：**Markdown 渲染要关注 XSS 风险，不能随意开放不可信 HTML。虚拟列表动态高度比固定高度复杂，因为滚动位置和占位高度要持续校正。这个回答可以连接到浏览器性能、流式协议和前端安全。

#### 2.1.15 预留 RAG：Embeddings、Qdrant、检索重排

**面试回答：**

> 这个项目里 RAG 相关文件更准确地说是预留扩展，不应该在面试里说成已经完整生产接入。当前主链路是“当前页面上下文 + SSE 流式 LLM”。如果升级为真正 RAG，我会离线切分 docs、demo、types 和组件源码，生成 embedding 写入 Qdrant；用户提问时先做向量检索，再按组件名、路由、文档类型和相似度重排，最后把 top-k 片段交给大模型回答。

**可以主动补充：**RAG 的价值是解决上下文长度和知识覆盖问题，但它会引入索引更新、分块策略、召回准确率、重排、权限和评估成本。面试里诚实说明“当前做到哪一步、下一步怎么做”，比夸大成完整知识库更成熟。

## 3. 目录结构怎么讲

面试官问“项目结构怎么设计”时，不要只报目录名，要说职责边界：

| 目录或文件 | 职责 | 面试表达 |
| --- | --- | --- |
| `src/components` | 组件库主体，每个组件独立维护 Vue 文件、类型和样式 | 组件库的基本单元是组件目录，而不是页面 |
| `src/components/*/types.ts` | 组件 props、emits、上下文、实例类型 | 公共 API 类型前置，利于维护和声明文件生成 |
| `src/hooks` | 跨组件复用逻辑，如 outside click、事件监听、z-index | 把 DOM 副作用和状态策略从组件中抽离 |
| `src/styles` | 全局 reset、变量、组件样式统一入口 | 组件库需要稳定样式入口和设计 token |
| `src/index.ts` | 库入口，负责全局安装、单组件导出、类型导出 | 组件库面向使用者的 API 门面 |
| `src/views`、`src/router` | 本地开发演示页 | 方便开发阶段调试组件行为 |
| `docs` | VitePress 文档和 demo | 组件库要让使用者看得懂、复制得走 |
| `src/test`、`*.test.ts` | 测试环境和测试用例 | 保障组件交互和公共 API 不回归 |
| `server` | 文档 AI 助手的 Node 服务 | 把前端文档上下文和 LLM 服务隔离，保护 API key |

## 4. 面试闭环总路线

回答任何问题时尽量按这个闭环走：

1. 先说它解决什么问题。
2. 再说项目里如何实现。
3. 再补充为什么选择这种方案。
4. 再主动指出局限和可优化点。
5. 最后把问题升到原理或工程化层面。

例如面试官问 `provide/inject`：

> 在普通父子组件里 props/emits 足够，但 Form、Collapse 这类组件不是简单父子，而是父组件要管理一组不确定数量的子项。项目里 Form 通过 `provide(formContextKey, context)` 提供 model、rules 和字段注册方法，FormItem 通过 `inject` 获取上下文，并在 mounted/unmounted 时向 Form 注册和注销。这样避免了层层传 props，也让 Input 可以通过 FormItem 的上下文触发校验。底层上，provide/inject 依赖组件实例链传递上下文，适合组件库内部协作，但不适合替代全局状态管理，因为它缺少显式数据流和调试能力。

## 5. Vue 3 相关面试闭环

### 5.1 为什么使用 Vue 3 + Composition API

项目落点：

- `Button.vue`、`Input.vue`、`Dialog.vue` 使用 `ref`、`computed`、`watch`、生命周期函数组织逻辑。
- `Rate/useRate.ts` 把评分状态抽成 composable。
- `Form`、`Collapse` 使用 `provide/inject` 做组合组件通信。

面试题：

**问：为什么组件库更适合用 Composition API？**

答：

> 组件库组件通常不是页面逻辑，而是多个能力的组合，比如 Input 同时有 v-model、清空、密码显隐、插槽、表单校验联动。Composition API 可以按能力组织代码，把焦点状态、受控值、校验触发、DOM 暴露拆开维护。相比 Options API，它更适合抽 composable，也更容易配合 TypeScript 做类型推导。

追问：

- `ref` 和 `reactive` 怎么选？
- `computed` 和 `watch` 怎么选？
- `<script setup>` 是运行时语法还是编译时语法？
- `defineProps`、`defineEmits`、`defineExpose` 底层是什么？

底层原理回答：

> `ref/reactive` 的核心是响应式依赖收集和触发更新。Vue 3 使用 Proxy 代理对象，读取时 track，修改时 trigger。`computed` 是带缓存的 effect，依赖不变时不会重新计算。`watch` 更适合处理副作用，比如同步外部 prop、触发表单校验、创建 Popper。`<script setup>` 和 `defineProps` 这类宏主要在编译阶段处理，不是运行时函数调用。

### 5.2 `v-model` 的实现

项目落点：

- `Input.vue` 使用 `modelValue` 和 `update:modelValue`。
- `Switch.vue` 支持 `activeValue`、`inactiveValue`。
- `Select.vue` 维护 `inputValue` 和 `selectOption`，选择后触发 `update:modelValue` 和 `change`。
- `Dialog.vue` 通过 `modelValue` 控制显示状态。

面试题：

**问：Vue 3 中组件的 v-model 是怎么实现的？**

答：

> Vue 3 的默认 v-model 本质上是父组件传入 `modelValue`，子组件通过 `emit('update:modelValue', nextValue)` 通知父组件更新。项目里的 Input 不能直接修改 props，所以内部维护 `inputValue`，监听 props.modelValue 保持同步，在 input 事件里同时更新内部值并 emit。这样子组件既能表现得像原生 input，又保持单向数据流。

追问：

- 为什么 props 不能直接改？
- 为什么 Input 要监听 `modelValue`？
- 受控组件和非受控组件有什么区别？
- 多个 v-model 怎么设计？

更成熟回答：

> 这个项目多数输入组件采用受控组件思路：外部 modelValue 是最终数据源，内部状态只是为了交互体验。这样 Form 能统一拿 model 做校验，外部也能强制重置值。缺点是要处理 props 和内部状态同步，否则容易出现回显不一致。

### 5.3 `provide/inject` 通信

项目落点：

- `Form` 提供 `model`、`rules`、`addField`、`removeField`、`validate`。
- `FormItem` 注入 Form 上下文，并向 Input 再提供 FormItem 上下文。
- `Collapse` 提供 `activeNames` 和 `handleItemClick`，`CollapseItem` 注入后判断是否激活。

面试题：

**问：为什么 Form 不用 props 一层层传？**

答：

> Form 的子组件数量和层级是不确定的，FormItem 可能包 Input，也可能包 Select，甚至中间还有自定义布局。如果用 props/emits 层层传，会让使用者的模板结构被组件库内部通信污染。provide/inject 更适合这种组合组件内部上下文传递。项目里还使用 `InjectionKey<FormContext>`，这样注入出来的上下文有类型约束。

追问：

- provide/inject 会不会破坏响应式？
- 为什么 key 用 Symbol？
- 它和 Pinia/Vuex 的边界是什么？
- FormItem 为什么要注册到 Form 的 `fields` 数组？

回答边界：

> provide/inject 适合组件树内的局部协议，不适合跨页面业务状态。Form 的 `fields` 注册表让 Form 可以统一调用所有 FormItem 的 validate、resetField、clearValidate，这就是组件库组合组件常见的父子协作模式。

## 6. TypeScript 相关面试闭环

### 6.1 Props 和 Emits 类型设计

项目落点：

- `Button/types.ts` 使用联合类型限制 `type`、`size`、`nativeType`。
- `Input/types.ts` 定义 `InputProps` 和函数重载式 `InputEmits`。
- `Form/types.ts` 使用 `ExtractPropTypes` 从运行时 props 推导类型。
- `Tooltip/types.ts` 使用 Popper 的 `Placement`、`Options` 类型。

面试题：

**问：TypeScript 在组件库里最大的价值是什么？**

答：

> 组件库的使用者依赖公共 API，TypeScript 的价值不是给内部变量标类型，而是把 props、emits、expose、slots、上下文协议都变成可约束的契约。比如 Button 的 type 只能是 `primary/success/info/warning/danger`，Form 的 rules 能复用 async-validator 的 RuleItem，Tooltip 的 placement 直接复用 Popper 类型，减少使用者传错值的概率。

追问：

- `interface` 和 `type` 怎么选？
- `PropType<T>` 为什么需要？
- `ExtractPropTypes` 有什么意义？
- `InjectionKey<T>` 为什么比字符串 key 好？

标准回答：

> `PropType<T>` 是把 TypeScript 类型传给 Vue 的运行时 props 声明，解决运行时 constructor 和静态类型之间的桥接。`ExtractPropTypes` 可以从 props 配置反推出组件内部使用的 props 类型，避免声明两份类型。`InjectionKey<T>` 则让 inject 返回值带上类型，避免上下文协议失控。

### 6.2 声明文件与类型出口

项目落点：

- `tsconfig.build.json` 开启 `declaration`、`emitDeclarationOnly`，输出到 `dist/types`。
- `package.json` 的 `types` 指向 `dist/types/index.d.ts`。
- `src/index.ts` 统一导出组件和类型。

面试题：

**问：组件库为什么要生成 `.d.ts`？**

答：

> 因为组件库最终是被别的项目安装使用的，使用者需要 props、emits、方法和工具类型的提示。`.d.ts` 是发布包的类型契约。项目中通过 `vue-tsc -p tsconfig.build.json` 生成声明文件，并在 package 的 `types` 字段暴露入口。

追问：

- `vue-tsc` 和 `tsc` 有什么区别？
- 为什么普通 `tsc` 不够处理 `.vue`？
- 类型声明如何和按需导出配合？

## 7. 组件库架构相关面试闭环

### 7.1 全局安装和单组件导出

项目落点：

- `src/index.ts` 实现 `withInstall`，给组件补 `install(app)`。
- `components` 数组支持 `app.use(TinyElement)` 全量安装。
- 同时导出 `Button`、`Input`、`Form` 等，支持局部引入。
- `Message` 挂到 `app.config.globalProperties.$message`。
- `MessageBox` 挂到 `$messageBox`。

面试题：

**问：组件库的入口文件应该做什么？**

答：

> 入口文件是组件库对外的门面。它要处理三件事：第一，全局安装，让用户 `app.use()` 后可以直接使用所有组件；第二，单组件导出，让用户可以按需引入；第三，导出公共类型，让 TypeScript 项目有完整提示。这个项目里 `withInstall` 把普通 SFC 包装成 Vue 插件，组件列表用于全量注册，最后统一 export。

追问：

- `app.component` 和 `app.use` 区别是什么？
- 为什么 Message 不只是普通组件？
- 全局注册和局部注册的优缺点是什么？

### 7.2 样式入口与主题 token

项目落点：

- `src/styles/variable.css` 定义 `--el-color-primary`、字号、边框、圆角、动画时长等 CSS 变量。
- `src/styles/index.css` 统一 import reset、variable 和所有组件样式。
- `package.json` 暴露 `./style.css`。

面试题：

**问：组件库样式系统怎么设计？**

答：

> 组件库样式要解决一致性和可覆盖性。项目里把颜色、字号、边框、圆角、动画时长抽成 CSS Variables，让组件样式使用统一 token。使用者可以通过覆盖变量实现主题定制。统一 `style.css` 入口则方便全量引入样式。

追问：

- CSS Variables 相比 Sass 变量有什么优势？
- 按需引入样式怎么做？
- 为什么 npm 包要考虑 `sideEffects`？

项目可优化点：

> 当前 `styles/index.css` 会引入所有组件样式，更偏全量样式入口。后续如果要做更完善的按需引入，可以为每个组件提供独立样式入口，并在 `package.json` 里声明 `sideEffects: ["**/*.css"]`，避免构建工具错误 tree-shaking 掉样式。

## 8. 表单体系面试闭环

项目落点：

- `Form.vue` 维护 `fields`，提供 validate、resetFields、clearValidate。
- `FormItem.vue` 负责读取当前字段值、过滤 trigger、调用 async-validator、维护校验状态。
- `Input.vue` 注入 FormItem 上下文，在 input/change/blur 时触发校验。

面试题：

**问：Form、FormItem、Input 三者怎么分工？**

答：

> Form 是控制中心，保存 model、rules 和所有字段实例；FormItem 是字段级控制器，知道自己的 prop、label、rules 和校验状态；Input 是具体输入控件，只负责值更新和在合适时机触发校验。这样职责清晰：Form 做聚合，FormItem 做字段逻辑，Input 做交互。

追问：

- 为什么要用 async-validator？
- trigger 是怎么生效的？
- resetFields 为什么要记录 initialValue？
- 如果异步校验有竞态怎么办？

更深入回答：

> async-validator 把校验规则抽象成 schema，可以支持 required、pattern、自定义 validator 和异步 Promise。项目里 FormItem 会按 trigger 过滤规则，再只校验当前 prop。后续如果要处理异步竞态，可以给每次校验加序号，只采纳最后一次结果，或者在输入频繁时做 debounce。

## 9. 浮层体系面试闭环

项目落点：

- `Tooltip.vue` 使用 Popper 的 `createPopper(reference, popper, options)`。
- 支持 hover、click、manual 三种模式。
- 使用 `useClickOutside` 监听外部点击。
- `Select.vue` 复用 Tooltip，并通过 manual 模式控制下拉面板。
- `Dialog.vue` 做遮罩、ESC 关闭、锁滚动、拖拽、`destroyOnClose`。
- `Message.vue` 使用 `useZIndex` 管理层级。

面试题：

**问：Tooltip 为什么要用 Popper，而不是自己算 top/left？**

答：

> 浮层定位看起来只是算坐标，但真实场景要处理滚动容器、窗口边界、不同 placement、偏移、箭头、溢出翻转等问题。项目里用 Popper 负责复杂定位，组件只维护显示状态和触发方式。Select 进一步复用 Tooltip，说明 Tooltip 在组件库里是底层弹层能力。

追问：

- Popper 的 modifier 是什么？
- 为什么 Select 要让下拉框宽度等于输入框？
- Tooltip 为什么 watch `isOpen` 时用 `flush: 'post'`？
- 为什么生产级 Dialog/Tooltip 常用 Teleport？

回答 Teleport：

> 当前项目的 Tooltip 和 Dialog 主要在组件当前位置渲染，适合教学和基础实现。但生产级弹层通常会 Teleport 到 body，避免父容器 `overflow: hidden`、`transform`、层叠上下文影响定位和 z-index。代价是焦点管理、事件回收、SSR 兼容和样式隔离要处理得更完整。

## 10. 命令式组件面试闭环

项目落点：

- `Message/method.ts` 使用 `h` 创建 VNode，`render` 动态挂载到 DOM。
- `Message/index.ts` 封装 `message.success/info/warning/error/closeAll`。
- `MessageBox/MessageBox.ts` 使用 `createApp` 动态挂载，并用 Promise 返回用户动作。

面试题：

**问：为什么 Message 适合做成命令式 API？**

答：

> Message 是一次性反馈，不适合要求用户在模板里手动写一个组件。命令式 API 可以让用户直接 `ElMessage.success('保存成功')`。内部通过 `h + render` 动态创建组件，加入实例队列，控制 z-index 和堆叠偏移，关闭时先改 visible 触发动画，再在动画结束后销毁 DOM。

追问：

- `h`、`render`、`createApp` 区别是什么？
- 为什么要传 `appContext`？
- MessageBox 为什么返回 Promise？
- 动态挂载如何避免内存泄漏？

成熟回答：

> `h/render` 更轻量，适合频繁创建的 Message；`createApp` 会创建独立应用实例，更适合 MessageBox 这种独立弹窗，但要注意它可能拿不到主应用的全局组件、provide 和插件，所以 Message 当前用 `appContext` 传递上下文是更完整的做法。

## 11. Vite 与构建工程化闭环

项目落点：

- 开发：`npm run dev` 使用 Vite。
- 普通构建：`npm run build` 先 `vue-tsc`，再 `vite build`。
- 库构建：`npm run build:lib` 使用 `vite build --mode lib`，再生成类型声明。
- `vite.config.ts` 中 mode 为 `lib` 时启用 `build.lib`。
- `rollupOptions.external = ['vue']`，避免把 Vue 打进组件库包。
- 输出 ES 和 UMD：`tiny-element.js`、`tiny-element.umd.js`。

面试题：

**问：为什么组件库构建时要把 Vue 设为 external？**

答：

> Vue 是宿主项目一定会安装的运行时，如果组件库把 Vue 打包进去，就可能出现重复 Vue 实例、包体变大、响应式上下文不一致等问题。把 Vue 放到 peerDependencies，并在 Rollup external 里排除，能让使用者项目共享自己的 Vue 版本。

追问：

- `dependencies` 和 `peerDependencies` 区别是什么？
- ES 产物和 UMD 产物分别给谁用？
- `exports` 字段解决什么问题？
- tree-shaking 的条件是什么？

标准回答：

> tree-shaking 依赖 ESM 静态结构和无副作用判断。这个项目提供 `module` 和 named exports，有利于组件按需引入。但样式 import 是副作用，不能随便被摇掉，所以真正完善发布时要声明 CSS sideEffects，并设计每个组件独立入口。

## 12. VitePress 文档站闭环

项目落点：

- `docs/.vitepress/config.ts` 配置 nav、sidebar、markdown demo preview。
- `docs/components/*.md` 写组件文档。
- `docs/demo/*/*.vue` 提供可运行示例。
- theme 中增强 Layout，把 `AiAssistant` 挂到页面底部。

面试题：

**问：组件库为什么需要文档站？**

答：

> 组件库不是只给开发者看源码，最终要让使用者快速理解 API、示例、边界和最佳实践。VitePress 适合写技术文档，结合 demo preview 可以把 Markdown 和 Vue 示例连起来。这个项目把 docs 和组件源码分离，但通过 alias 引用 `src`，保证文档示例接近真实使用方式。

追问：

- 文档 demo 如何避免和源码脱节？
- 为什么 VitePress 的主题层可以扩展 AI 助手？
- 文档站构建和组件库构建有什么区别？

## 13. 测试闭环

项目落点：

- `vitest.config.ts` 使用 jsdom 模拟浏览器环境。
- `src/test/setup.ts` mock `ResizeObserver`，注册 FontAwesome 图标库，并在 afterEach 清理 DOM。
- `Button.test.ts` 测类名、disabled、icon、loading。
- `Tooltip.test.ts` mock Popper，使用 fake timers 测 debounce 和浮层显示。
- `InteractiveComponents.test.ts` 测 Collapse、Dialog、Dropdown、Select、Switch、Tooltip。
- `FormAndInput.test.ts` 测 v-model、密码显隐、Form 校验。

面试题：

**问：组件库测试重点测什么？**

答：

> 组件库测试重点不是截图，而是公共 API 是否稳定：props 是否影响渲染，emits 是否正确触发，插槽是否优先，命令式方法是否可用，表单校验是否按预期 reject/resolve。像 Popper 这种第三方定位算法不需要自己测坐标，项目里选择 mock `createPopper`，只验证组件是否在正确时机调用定位能力。

追问：

- 为什么用 jsdom？
- fake timers 解决什么问题？
- 为什么要清理 document.body？
- 单元测试、组件测试、E2E 测试边界是什么？

## 14. AI 助手与服务端闭环

项目落点：

- `AiAssistant.vue` 采集当前 VitePress 页面标题、heading、table、code 和可见文本。
- 前端请求 `/api/chat`，VitePress dev server 代理到 `127.0.0.1:3030`。
- `server/src/app.ts` 用 Express 接收问题，拼 system prompt，请求 Qwen 兼容 OpenAI 的 `/chat/completions`。
- 服务端用 SSE 向浏览器流式返回 `delta`、`done`、`error`。
- 前端用 `ReadableStream.getReader()` 读取流，做打字机效果。
- 前端对消息列表做虚拟滚动，使用 `ResizeObserver` 动态记录消息高度。
- `server/src/services` 中有 knowledge、embeddings、qdrant、rag 的预留实现，但当前 `server/tsconfig.json` 只编译 `app.ts/config.ts/types.ts`，主服务实际是“当前页面上下文 + 流式 LLM”，不是完整启用的 Qdrant RAG。

面试题：

**问：你这个 AI 文档助手完整链路是什么？**

答：

> 浏览器端先采集当前文档页面上下文，包括标题、API 表格、代码示例和可见文本，再把用户问题、历史消息和页面上下文发给 Node 服务。Node 服务负责拼 prompt，并把私有 API key 放在服务端调用大模型，避免泄露到浏览器。返回时使用 SSE 流式传输，前端逐 chunk 解析并渲染 Markdown。

追问：

- 为什么 API key 不能放前端？
- SSE 和 WebSocket 怎么选？
- 为什么要限制上下文长度？
- 如果升级成真正 RAG，你会怎么做？

升级回答：

> 真正 RAG 会离线切分 docs、demo、types，生成 embedding 写入向量库；用户提问时先向量检索，再按组件名、route、sourceType 重排，最后把 top-k 片段交给 LLM。当前仓库已经有部分 services 代码，但主服务还没完全接入，这是可以继续完善的工程点。

## 15. 前端性能优化闭环

面试官问性能优化，不要只背“懒加载、防抖、节流”。要结合项目从五层回答。

### 15.1 组件运行时优化

项目已有做法：

- `computed` 缓存派生状态，如 Button 类名、FormItem required、Select placeholder。
- `watch` 只处理副作用，如同步 props、打开弹层后创建 Popper。
- `Select` 使用 debounce 处理远程搜索。
- `Message` 用 `shallowReactive` 管理实例队列，避免深层响应式开销。
- `useEventListener`、`useClickOutside` 在卸载时移除监听，避免内存泄漏。
- `Dialog` 拖拽使用 `transform`，比频繁改 top/left 更接近合成层更新。
- `AiAssistant` 对消息列表做虚拟滚动，避免长对话渲染大量 DOM。

面试题：

**问：你在项目里做过哪些性能优化？**

答：

> 我会分运行时、构建产物、网络和浏览器渲染四层讲。运行时上，Select 远程搜索用 debounce，Message 实例队列用 shallowReactive，AI 助手长列表用虚拟滚动，事件监听封装成 hook 并在卸载时清理。构建上，库模式 external Vue，配合 named exports 支持 tree-shaking。浏览器渲染上，Dialog 拖拽用 transform，Tooltip 在 DOM 更新后再创建 Popper，减少错误测量。网络上，AI 助手用 SSE 流式返回，用户不用等完整回答。

追问：

- debounce 和 throttle 区别？
- 虚拟列表怎么处理动态高度？
- transform 为什么通常比 top/left 更适合动画？
- shallowReactive 和 reactive 有什么区别？

### 15.2 构建与包体优化

项目已有做法：

- Vite 库模式构建 ES/UMD。
- Vue external，减少包体和重复运行时。
- `lodash-es` 是 ESM，更利于 tree-shaking。
- 路由 demo 使用动态 import，开发演示页可懒加载。

可优化点：

- 明确 `sideEffects`，避免 CSS 被错误摇掉。
- 为每个组件生成独立入口和样式入口。
- 检查未使用依赖，例如当前安装了 `@floating-ui/vue`，但 Tooltip 实际使用的是 Popper。
- 增加 bundle analyzer、size limit 或 CI 体积检查。

### 15.3 浏览器渲染优化

面试题：

**问：重排、重绘、合成分别是什么？项目里哪里体现？**

答：

> 重排是布局计算变化，比如宽高、位置、display 改变；重绘是颜色、背景等视觉变化；合成是浏览器把已经绘制好的图层做 transform/opacity 合成。项目里 Dialog 拖拽用 `transform: translate(...)`，通常可以减少布局影响；Tooltip 打开后要测量 trigger 和 popper，所以需要等 DOM 更新后再创建 Popper，否则会拿不到正确尺寸。

追问：

- Popper 为什么可能触发布局测量？
- 如何避免 layout thrashing？
- 动画为什么优先用 transform/opacity？

### 15.4 网络与流式体验优化

项目已有做法：

- AI 服务用 SSE，边生成边显示。
- 服务端 `trimContext` 限制 prompt 上下文长度。
- VitePress 通过本地 proxy 转发 `/api/chat`，避免前端硬编码服务地址。

追问：

- SSE 与 WebSocket、轮询的区别？
- fetch stream 如何解析？
- 为什么大模型上下文需要裁剪？

## 16. 浏览器原理面试闭环

### 16.1 事件循环与 Vue 更新

项目落点：

- `Tooltip.test.ts` 里通过 fake timers 和多次 `nextTick` 等待 debounce、DOM 更新、post flush watch。
- `AiAssistant.vue` 多处用 `nextTick` 保证 DOM 渲染后滚动到底部。

面试题：

**问：为什么有时候要 `await nextTick()`？**

答：

> Vue 的响应式状态变化不会立即同步更新 DOM，而是进入调度队列，在同一轮事件循环里批量更新。`nextTick` 能等 DOM patch 完成后再读写 DOM。Tooltip 打开时先让 `isOpen` 变 true，DOM 里出现 popper 后，再创建 Popper 实例计算位置，所以 watch 使用 `flush: 'post'`。

追问：

- 宏任务和微任务区别？
- Vue 为什么要批量更新？
- `watch` 的 `flush: pre/post/sync` 有什么区别？

### 16.2 事件传播与点击外部关闭

项目落点：

- `useClickOutside` 在 document 上监听 click，通过 `contains(e.target)` 判断是否点击外部。
- `Select` 对选项点击使用 `@click.stop`，避免触发外层关闭逻辑。
- `Dialog` 遮罩点击通过 `event.target === event.currentTarget` 判断是否点在遮罩本身。

面试题：

**问：点击外部关闭是怎么实现的？**

答：

> 核心是利用事件冒泡，在 document 监听点击事件，再判断事件目标是否包含在当前组件根节点里。如果不包含，就认为点到了外部。项目里还要结合 `.stop` 防止内部选项点击冒泡影响外层逻辑。Dialog 遮罩则通过 target 和 currentTarget 判断是不是直接点在遮罩上。

追问：

- 捕获和冒泡区别？
- `.stop` 做了什么？
- Shadow DOM 或 Teleport 场景要注意什么？

### 16.3 CORS、代理与服务端安全

项目落点：

- VitePress dev server proxy 把 `/api/chat` 转发到 `127.0.0.1:3030`。
- Express 设置 CORS header。
- API key 只在 server `.env` 中读取，不暴露给浏览器。

面试题：

**问：为什么大模型请求要走服务端代理？**

答：

> 前端代码会被用户下载，API key 放前端一定会泄露。服务端代理能把鉴权信息留在服务器，同时可以做限流、日志、上下文裁剪、错误处理和流式转发。开发环境下用 VitePress proxy 统一路径，避免浏览器跨域问题。

## 17. 高频技术栈面试题速查

### Vue 3

**问：Vue 3 响应式相比 Vue 2 有什么变化？**

答：Vue 3 使用 Proxy 代理对象，能更自然地监听新增属性、删除属性、数组索引等变化；Vue 2 主要基于 `Object.defineProperty`，需要对对象属性逐个劫持。Proxy 不能 polyfill 到旧浏览器，但能力更完整。

**问：computed 和 watch 怎么选？**

答：computed 用于同步派生值，有缓存，不应该写副作用；watch 用于响应状态变化后的副作用，比如请求、DOM 操作、同步内部状态、触发表单校验。

**问：为什么组件库里经常用 defineExpose？**

答：组件库有些能力需要通过实例暴露给父组件，比如 Form 暴露 validate/resetFields，Tooltip 暴露 show/hide，Dialog 暴露 handleClose/resetPosition。默认 `<script setup>` 内部变量不会暴露，必须显式 defineExpose。

### TypeScript

**问：组件库类型设计要关注什么？**

答：关注公共 API，而不是只给内部变量加类型。props、emits、slots、expose、上下文、命令式方法、发布包声明文件都要有类型。

**问：为什么 `InjectionKey<T>` 重要？**

答：它把 provide/inject 的 key 和上下文类型绑定起来，减少字符串冲突，也让 inject 结果具备类型推导。

### 工程化

**问：为什么需要 `peerDependencies`？**

答：组件库依赖宿主项目的 Vue，使用 peerDependencies 表达“你需要安装兼容版本的 Vue”。这样避免打包重复 Vue，也避免运行时上下文不一致。

**问：`main/module/types/exports` 分别是什么？**

答：`main` 通常给 CommonJS 或 UMD 使用，`module` 给 ESM 构建工具使用，`types` 给 TypeScript 类型入口，`exports` 明确包的可访问入口，避免使用者引用内部不稳定路径。

**问：组件库如何支持按需引入？**

答：首先要有 ESM named exports，其次构建产物要可 tree-shaking，再配合每个组件独立入口和样式入口。CSS 属于副作用，需要正确声明 sideEffects。

### 浏览器

**问：输入 URL 到页面显示发生了什么？**

答：DNS 解析、TCP/TLS 连接、发送 HTTP 请求、服务器响应 HTML、浏览器解析 HTML 构建 DOM、解析 CSS 构建 CSSOM、合成 render tree、布局、绘制、合成。遇到 JS 可能阻塞解析，现代构建工具会通过模块、预加载、缓存优化加载路径。

**问：重排和重绘如何优化？**

答：减少频繁读写布局属性，批量 DOM 操作，动画使用 transform/opacity，避免复杂选择器和过深 DOM，长列表使用虚拟滚动，弹层测量放到 DOM 更新后。

### 测试

**问：为什么不测试 Popper 的具体坐标？**

答：Popper 是第三方库，它自己的定位算法不属于项目单元测试范围。项目要测的是我们有没有在正确时机创建 Popper、传入正确选项、显示隐藏逻辑是否正确。

### AI 助手

**问：SSE 和 WebSocket 怎么选？**

答：如果是服务端单向持续推送，比如大模型 token 流，SSE 简单、基于 HTTP、浏览器支持好。WebSocket 适合强双向实时通信，比如协同编辑、游戏、聊天室。

## 18. 可以主动讲的性能优化案例

1. **Select 远程搜索防抖**
   - 项目落点：`Select.vue` 的 `debounceOnFilter`。
   - 面试说法：避免用户每输入一个字符都触发远程请求，降低服务端压力和竞态概率。

2. **Message 队列浅响应式**
   - 项目落点：`Message/method.ts` 的 `shallowReactive([])`。
   - 面试说法：实例队列只关心数组增删，不需要深度追踪每个 vnode/vm 内部字段。

3. **AI 助手虚拟列表**
   - 项目落点：`AiAssistant.vue` 的 `visibleRange`、`virtualRows`、`ResizeObserver`。
   - 面试说法：长对话不一次性渲染所有 DOM，动态高度用 ResizeObserver 回填真实高度。

4. **Dialog 拖拽使用 transform**
   - 项目落点：`dialogStyle` 中的 `transform: translate(...)`。
   - 面试说法：拖拽属于高频交互，用 transform 通常比改 top/left 更利于浏览器合成。

5. **路由 demo 懒加载**
   - 项目落点：`src/router/index.ts` 的 `component: () => import(...)`。
   - 面试说法：演示页按路由拆分，首屏不用加载所有组件 demo。

## 19. 当前项目不足与诚实答法

这部分很重要。面试不是把项目说得完美，而是证明你知道边界。

| 不足 | 诚实说法 | 优化方向 |
| --- | --- | --- |
| 弹层未使用 Teleport | 当前实现更偏教学版，能说明浮层状态和定位，但生产级要避免父容器影响 | Tooltip/Dialog teleport 到 body，补焦点管理和 a11y |
| 样式按需不完整 | 当前有全量 `style.css`，适合快速使用 | 组件独立样式入口，声明 CSS sideEffects |
| RAG 服务未完整接入主服务 | 当前实际是页面上下文 + SSE LLM，RAG 文件是预留能力 | 完善 config、tsconfig、reindex、Qdrant 检索 API |
| 测试还可扩展 | 已覆盖核心交互，但缺少覆盖率门禁和 E2E | 加 coverage、CI、Playwright、可访问性测试 |
| 部分组件 API 还可完善 | DatePicker 更像 Calendar 基础版，Select 还有键盘导航空间 | 补键盘操作、ARIA、更多边界状态 |
| MessageBox appContext 继承不足 | createApp 独立挂载可能拿不到主 app 上下文 | 参考 Message 传入 appContext 或统一命令式挂载策略 |

## 20. 简历可写亮点

可以写：

- 基于 Vue 3 + TypeScript 设计并实现组件库，封装 Button、Input、Form、Select、Tooltip、Dialog、Message 等组件，支持全局安装、单组件导出和类型声明生成。
- 设计 Form/FormItem/Input 联动校验体系，基于 provide/inject 建立表单上下文，通过 async-validator 支持字段级规则校验、触发时机过滤、重置与清空校验状态。
- 封装 Tooltip 浮层基础能力，基于 Popper.js 支持 hover/click/manual 触发、外部点击关闭，并复用于 Select/Dropdown 等复合组件。
- 实现 Message/MessageBox 命令式反馈组件，使用 Vue `h/render/createApp` 动态挂载，管理实例队列、z-index、关闭动画和 Promise 交互结果。
- 搭建 VitePress 组件文档站和 demo 预览体系，接入文档页 AI 问答助手，基于 Express + SSE 实现流式回答和前端 Markdown 渲染。
- 使用 Vitest + Vue Test Utils 编写组件单元测试，覆盖 props 渲染、emits、插槽优先级、表单校验、弹层交互和定时器逻辑。

不要夸大的点：

- 不要说“完整复刻 Element Plus”。
- 不要说“实现了完整生产级 RAG”，当前主服务更准确是“文档上下文问答助手，预留 RAG 扩展”。
- 不要说“实现了完整按需加载样式”，当前更偏全量样式入口。

## 21. 面试自我介绍模板

你可以这样串起来：

> 我这个项目是一个仿 Element Plus 思路的 Vue 3 + TypeScript 组件库。项目里我重点做了三层能力：第一是组件设计，包括 Button、Input、Form、Select、Tooltip、Dialog、Message 等组件；第二是组件库工程化，包括全局安装、单组件导出、类型声明、Vite 库模式构建、VitePress 文档和 Vitest 测试；第三是一些更工程化的扩展，比如文档站 AI 助手，前端采集当前文档上下文，服务端用 SSE 流式返回模型回答。  
>  
> 如果展开讲，我会重点讲 Form 的 provide/inject 注册表和 async-validator 校验、Tooltip/Select 的浮层复用、Message 的命令式动态挂载，以及组件库发布时 external Vue、peerDependencies、exports 和样式 sideEffects 这些工程问题。

## 22. 复习顺序建议

1. 先掌握 `src/index.ts`：知道组件库如何安装、导出和发布。
2. 再掌握 Form 体系：这是最能体现组件库设计深度的模块。
3. 再掌握 Tooltip/Select/Dialog/Message：覆盖浮层、命令式组件、DOM 副作用。
4. 再掌握 Vite 构建：能解释 `external`、`exports`、`types`、tree-shaking。
5. 再掌握测试：能讲 mock、fake timers、jsdom 和测试边界。
6. 最后准备性能和浏览器原理：把项目实现和底层机制连起来。

真正面试时，最好的状态不是“我背过这个题”，而是“这个问题在我的项目里有具体场景，我知道为什么这样做，也知道下一步怎么做得更好”。
