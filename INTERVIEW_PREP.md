# TinyElement 项目面试准备文档

## 1. 项目一句话介绍

这是一个基于 Vue 3 + TypeScript + Vite 搭建的轻量级组件库项目，核心目标是从 0 到 1 完成“组件开发 + 文档站点 + 测试 + 打包发布 + AI 文档问答”这一整套前端工程闭环。

## 2. 项目定位

### 2.1 我在面试里怎么定义这个项目

不要把它说成“普通练手 demo”，更准确的说法是：

> 这是一个偏工程化的组件库项目，我主要通过它系统训练了组件抽象能力、TypeScript 类型设计、Vue 组件通信、函数式弹层封装、文档站建设，以及前端项目的测试和交付能力。

### 2.2 项目真实边界

- 这是一个组件库，不是复杂业务后台系统。
- 它更强调“通用 UI 能力抽象”和“可复用组件设计”。
- 除了组件本体，项目还补了文档站、示例、测试和 RAG 问答服务，所以完整度比普通组件练习更高。

## 3. 项目全景图

### 3.1 技术栈

- 前端框架：Vue 3
- 语言：TypeScript
- 构建工具：Vite
- 文档站：VitePress
- 路由：Vue Router
- 测试：Vitest + Vue Test Utils + jsdom
- 表单校验：async-validator
- 浮层定位：@popperjs/core
- 图标：Font Awesome
- AI 问答服务：Node.js + Qdrant + OpenAI-compatible API

### 3.2 当前项目包含的能力

- 组件源码：`src/components`
- 本地演示页：`src/views` + `src/router`
- 文档站：`docs`
- 文档站主题增强与 AI 助手：`docs/.vitepress/theme`
- 组件库统一导出入口：`src/index.ts`
- 库模式打包：`vite.config.ts`
- 类型声明输出：`tsconfig.build.json`
- RAG 服务：`server/src`
- 自动化测试：`src/components/*.test.ts`

### 3.3 可以说给面试官听的成果

- 组件文档页 17 个以上，覆盖基础、反馈、数据输入三类常见 UI 组件。
- 已实现 Button、Alert、Collapse、Tooltip、Dropdown、Input、Select、Form、Dialog、Message、MessageBox、Switch、DatePicker 等核心组件。
- 已补充 4 组测试文件，共 20 个测试用例，当前测试可以通过。
- 组件库支持样式统一导出、ESM/UMD 双格式构建和类型声明输出。
- 文档站除了基础 demo，还接入了基于文档、示例和类型定义的 AI 问答助手。

## 4. 30 秒 / 60 秒 / 90 秒项目介绍模板

### 4.1 30 秒版本

我做的是一个基于 Vue3、TypeScript 和 Vite 的轻量组件库项目，目标不是只写几个组件，而是完整跑通组件开发、统一导出、文档展示、测试验证和库模式打包这套流程。项目里我实现了 Form、Select、Dialog、Tooltip、Message 这类相对复杂的组件，还给 VitePress 文档站加了一个基于向量检索的 AI 问答功能。

### 4.2 60 秒版本

这个项目本质上是一个 TinyElement 组件库。我先用 Vue3 + TypeScript 搭建组件层，用统一的 `install` 和导出入口支持全量注册；然后用 Vite 的库模式输出 ESM、UMD 和类型声明；文档部分用 VitePress 组织组件说明和 demo 预览；测试部分用 Vitest 去覆盖基础渲染、交互行为和表单校验。项目里我重点做了几个复杂点，比如 Form 和 FormItem 的 provide/inject 通信、Tooltip 和 Dropdown 的浮层定位、Select 的可过滤和远程搜索、以及 Message/MessageBox 这种函数式调用组件。后面我还扩展了一个 Node 服务，把文档、示例和类型定义切片后写入 Qdrant，给文档站加了 AI 检索问答。

### 4.3 90 秒版本

我把这个项目当成“组件库工程化实践”来做。前端部分用 Vue3 组合式 API 和 TypeScript 做组件抽象，像 Button、Alert 这种基础组件主要关注 props 设计和样式体系；像 Form、Select、Dialog、Tooltip、Dropdown、Message 这些复杂组件，则重点处理组件通信、状态同步、弹层定位、函数式挂载和可测试性。工程化上，我通过 `src/index.ts` 做统一导出，通过 `vite.config.ts` 开启库模式，把 Vue 设成 external，输出 ESM 和 UMD；再通过 `tsconfig.build.json` 输出类型声明。文档部分我用 VitePress 管理组件文档和 demo，同时在主题层注入 AI Assistant，通过 `/api/rag/ask` 调用 Node 服务。服务端会把组件文档、demo 和 `types.ts` 统一切片，做 embedding，写入 Qdrant，在提问时结合路由和组件名做检索，再让大模型基于上下文生成回答。这样项目最终形成了组件开发、文档展示、测试验证和智能检索的一整套闭环。

## 5. 项目亮点拆解

### 5.1 亮点一：不是只写组件，而是做了“组件库闭环”

- 有组件源码。
- 有统一导出和安装机制。
- 有 demo 演示和文档站。
- 有测试。
- 有库模式打包和类型输出。
- 还有 AI 文档问答扩展。

### 5.2 亮点二：复杂组件不止是 UI，还处理了交互和状态

- `Form` / `FormItem`：字段注册、校验、重置、清空校验状态。
- `Tooltip` / `Dropdown` / `Select`：Popper 定位、触发方式切换、点击外部关闭。
- `Dialog`：遮罩、ESC 关闭、锁滚动、拖拽、生命周期事件。
- `Message` / `MessageBox`：函数式调用、动态挂载、实例管理。

### 5.3 亮点三：文档站做了智能化增强

- 不是静态说明页。
- AI 助手会结合当前路由和组件名做检索。
- 知识源不仅有 markdown 文档，还有 demo 源码和类型定义。

## 6. 核心架构理解

### 6.1 前端组件层

- 每个组件独立目录，通常包含 `*.vue`、`types.ts`、`style.css`、`index.ts`。
- `types.ts` 负责 props、emits、实例类型定义。
- `index.ts` 负责 `install`，保证可以 `app.use()`。
- `src/index.ts` 做统一导出，并把样式入口统一引入。

### 6.2 工程化层

- Vite 普通模式用于本地开发和 demo 预览。
- Vite `lib` 模式用于输出组件库产物。
- `vue-tsc` + `tsconfig.build.json` 负责生成声明文件。
- `exports` 字段暴露库入口和样式入口。

### 6.3 文档层

- 文档用 `docs/components/*.md` 组织。
- demo 用 `docs/demo/*/*.vue` 存放。
- 通过 `@vitepress-demo-preview` 在文档中预览组件示例。
- 在主题层挂载 `AiAssistant.vue`，实现文档问答入口。

### 6.4 服务层

- Node 原生 `http` 创建服务。
- `knowledge.ts` 负责扫描 docs、demo、types，切成知识块。
- `embeddings.ts` 生成向量。
- `qdrant.ts` 负责集合创建、向量写入和检索。
- `llm.ts` 基于检索结果组织上下文，让模型只根据项目资料回答。

## 7. 高频面试题与 STAR 回答

下面这部分最重要。回答时尽量用“我当时为什么这么做、怎么做、做完有什么结果”去说，不要只背概念。

### 7.1 请你介绍一下这个项目

**S（Situation）**

我想找一个既能体现前端基础能力，也能体现工程化思维的项目，所以没有只做页面临摹，而是选择做一个可复用的组件库。

**T（Task）**

目标是从 0 到 1 做出一个可演示、可测试、可打包的 Vue3 组件库，并且尽量覆盖常见 UI 组件和复杂交互场景。

**A（Action）**

我用 Vue3 + TypeScript + Vite 搭了基础工程，把组件按基础、反馈、数据输入三类拆分；通过 `src/index.ts` 统一导出，支持全量注册；通过 VitePress 建文档站和 demo；再用 Vitest 给组件补测试。后面我又扩展了一个 Node 服务，把文档、demo 和类型定义接到 RAG 流程里，给文档站增加 AI 问答能力。

**R（Result）**

最终项目形成了“组件源码 + 文档 + 示例 + 测试 + 打包 + AI 文档问答”的完整闭环，不只是展示 UI，而是更接近真实组件库项目的交付形态。

### 7.2 为什么选择 Vue3 + TypeScript + Vite？

**S**

这个项目组件数量多、状态和交互也比较复杂，如果只是用 JavaScript，后期维护和重构成本会比较高。

**T**

我希望技术选型既能提升开发效率，又能保证组件接口清晰、类型安全，并且适合做库模式构建。

**A**

我选择 Vue3，是因为组合式 API 很适合抽离逻辑，比如表单校验、浮层显示、z-index 管理都能拆成更清晰的逻辑块；选择 TypeScript，是为了把 props、emits、实例暴露、表单规则这些能力前置到类型层；选择 Vite，是因为它本地开发快，同时支持库模式构建，方便输出 ESM 和 UMD。

**R**

这套技术组合让我既能快速迭代组件，又能通过类型定义约束 API，项目后期在做统一导出、声明文件输出和复杂组件维护时更稳定。

### 7.3 你是怎么设计组件库导出机制的？

**S**

如果每个组件只能局部引入，使用方式会比较分散；如果只能全量注册，又不够灵活。

**T**

我要让组件库既支持整库 `app.use()`，也支持单个组件按需引入。

**A**

我在每个组件的 `index.ts` 里给组件挂上 `install` 方法，让它具备插件能力；在 `src/index.ts` 里统一收集组件，提供默认导出的 installer，同时也把各个组件单独导出。像 `Button`、`Container`、`Dialog`、`Tooltip` 都用了类似模式。样式方面统一在 `src/styles/index.css` 里集中引入，保证整库安装时样式也会生效。

**R**

这样最终对外同时支持整库安装和单组件导入，使用姿势更接近成熟组件库，也方便后续继续扩展组件数量。

### 7.4 你在项目里是怎么做组件通信的？

**S**

像 `Form/FormItem`、`Collapse/CollapseItem` 这种父子协作组件，如果只靠 props 一层层传会比较别扭，也不利于后续扩展。

**T**

我要让父组件能统一管理状态，子组件又能拿到上下文能力，比如注册字段、触发校验、更新折叠项状态。

**A**

我主要用了 Vue 的 `provide/inject`。比如 `Collapse` 提供 `activeNames` 和 `handleItemClick`，`CollapseItem` 通过注入去判断当前是否激活并触发切换。`Form` 里则更进一步，不只是传状态，还维护 `fields` 注册表，给 `FormItem` 提供 `addField`、`removeField`、`validate`、`resetFields`、`clearValidate` 等方法；而 `FormItem` 再继续把自己的 `validate` 能力通过 `formItemContextKey` 提供给 `Input`，形成两层上下文。

**R**

结果是组件之间的职责边界更清晰，父组件做统一调度，子组件专注自身行为，复杂表单场景也更容易扩展。

### 7.5 Form 表单校验是怎么实现的？

**S**

表单是组件库里典型的复杂组件，不只是渲染，还要处理规则校验、错误提示、字段重置和外部调用。

**T**

我要实现一个可以通过 `rules` 和 `prop` 建立映射的校验机制，并且支持单字段校验和整表校验。

**A**

我在 `Form` 中维护字段实例数组，`FormItem` 在挂载时注册自己，在卸载时移除。`FormItem` 根据自己的 `prop` 去 `Form` 的 `model` 和 `rules` 里取值和规则，再把带有 `trigger` 的规则过滤后交给 `async-validator`。`Input` 在 `input`、`change`、`blur` 事件里，根据 `validateEvent` 决定是否调用 `formItemContext.validate(trigger)`。这样就把输入行为和校验行为串起来了。

**R**

最后实现了字段级和表单级校验、错误状态展示、重置字段和清空校验状态这些核心能力，测试里也覆盖了无效校验到修正后通过的完整流程。

### 7.6 Tooltip、Dropdown、Select 这一类浮层组件你是怎么设计的？

**S**

这类组件的难点不在静态 UI，而在于定位、显示隐藏时机、点击外部关闭、以及和输入交互联动。

**T**

我要让这些组件在基础能力上尽量复用，避免每个组件都各写一套浮层逻辑。

**A**

我先把 `Tooltip` 做成底层浮层能力组件，负责 trigger、placement、openDelay、closeDelay、manual 控制、click outside 和 Popper 定位。然后 `Dropdown` 直接复用 `Tooltip`，只关注菜单内容渲染和菜单项点击后的 select 事件。`Select` 再继续复用 `Tooltip + Input`，在此基础上补了过滤、远程搜索、同宽弹层、清空选项、hover 显示 clear 图标等行为。

**R**

这样复杂浮层能力被拆成了“底层定位能力 + 上层业务交互”的两层结构，复用度更高，也更方便测试和维护。

### 7.7 Select 组件里你觉得最值得讲的点是什么？

**S**

Select 看起来是简单下拉框，但实际上它同时涉及输入框、弹层、选项状态、过滤逻辑和清空交互。

**T**

我要让它支持基础单选，同时兼容 `filterable`、自定义过滤、远程搜索、清空和自定义渲染 label。

**A**

我把内部状态拆成 `inputValue`、`selectOption`、`mouseHover`、`loading` 四块；通过 `findOption` 和 `watch` 保证 props 和内部状态同步；过滤逻辑上优先走 `filterMethod`，远程场景走 `remoteMethod`，都没有时才走默认 `label.includes()`；为了避免频繁请求，我还用 `debounce` 做了防抖；另外通过 Popper 自定义 modifier 让弹层宽度跟输入框保持一致。

**R**

最终 Select 不只是能选值，还具备了接近业务可用组件的过滤和远程搜索能力，这也是我在这个项目里抽象交互最完整的组件之一。

### 7.8 Dialog 是怎么实现拖拽、关闭和滚动锁定的？

**S**

Dialog 的使用频率高，用户对体验也敏感，比如遮罩点击关闭、ESC 关闭、弹窗拖拽和页面锁滚动这些都是常见需求。

**T**

我要做一个既能满足常规弹窗，又支持拖拽和生命周期事件的 Dialog。

**A**

我先用 `modelValue` 控制显示，再加上 `visible` 和 `rendered` 区分“当前是否可见”和“是否需要销毁 DOM”；遮罩点击和 ESC 分别走 `closeOnClickModal`、`closeOnPressEscape` 配置；页面锁滚动通过记录 `document.body.style.overflow` 并在打开时设成 `hidden`、关闭后恢复；拖拽则通过记录起始坐标和位移，在 `mousemove` 中更新 `transform: translate(x, y)`。

**R**

最后这个 Dialog 不只是一个简单模态框，而是具备可配置关闭策略、动画生命周期、拖拽能力和滚动管理的完整组件，适合在面试里重点展开。

### 7.9 Message 和 MessageBox 这种函数式组件你是怎么做的？

**S**

这类组件和普通声明式组件不一样，业务里更常见的是 `Message.success()` 或 `MessageBox.confirm()` 这种直接调用方式。

**T**

我要让它们脱离页面模板独立创建，同时还能和当前 Vue 应用上下文打通。

**A**

`Message` 我用了 `h + render` 动态创建 vnode，并维护一个 `instances` 数组管理所有消息实例。每条消息都会拿到唯一 id，通过 `getLastBottomOffset` 计算堆叠位置，再结合 `useZIndex` 统一管理层级。`MessageBox` 则用了 `createApp` 动态挂载组件，并用 `watch(vm.state)` 监听用户最终是 `confirm`、`cancel` 还是 `close`，再把动作 resolve 给调用方。

**R**

这样项目同时支持声明式组件和函数式弹层调用，更贴近真实业务中的组件库使用方式，也体现了我对 Vue 渲染机制和实例生命周期的理解。

### 7.10 你为什么给文档站加了 AI 问答？

**S**

传统组件文档站的查找方式主要靠目录和搜索，但当组件变多以后，用户经常不知道该看哪个文档、哪个 demo。

**T**

我想做一个更贴近真实使用场景的增强功能，让用户能直接用自然语言提问。

**A**

我在 VitePress 主题层增加了 `AiAssistant.vue`，它会把用户问题、最近聊天记录和当前路由发到 `/api/rag/ask`。服务端会扫描组件文档、demo 源码和 `types.ts`，统一做知识切片；提问时先判断可能的组件名，再结合当前路由和向量检索结果做召回，最后把这些上下文拼给兼容 OpenAI 接口的大模型，要求模型只能基于给定资料回答，并返回引用来源。

**R**

最后文档站不只是“展示组件”，而是具备了“可问答的组件知识库”能力，这让项目的差异化和完整度都更强。

### 7.11 这个项目里你怎么保证代码质量？

**S**

组件库的一个问题是“看起来能用”不代表“边界情况可靠”，尤其是交互组件非常容易出现回归。

**T**

我要把质量保障做在开发流程里，而不是完全靠手工点页面。

**A**

我主要做了三层保证。第一层是 TypeScript，把 props、emits、实例暴露和上下文对象都做了类型约束；第二层是 Vitest + Vue Test Utils，覆盖基础渲染、事件触发、浮层交互、表单校验、函数式组件行为等；第三层是文档 demo，本身也是一种可视化回归检查。实际测试里目前有 4 组测试文件、20 个测试用例可以通过。

**R**

这样项目不是停留在“能跑”，而是有基本的质量保障体系，面试时也能证明我不是只会写 happy path。

### 7.12 你觉得项目里最难的部分是什么？

**S**

对我来说，最难的不是 Button 这种单组件，而是跨组件协作和函数式弹层这两类问题。

**T**

我要解决的核心是：一方面让表单和输入框形成联动，另一方面让 Message 和 MessageBox 这类脱离模板的组件也能正常管理生命周期。

**A**

在表单部分，我通过 `provide/inject + 字段注册机制 + async-validator` 把 Form、FormItem、Input 串起来；在函数式弹层部分，我研究了 Vue 的 `h`、`render`、`createApp` 和组件暴露机制，把实例管理、关闭逻辑、z-index 和 Promise 返回值都统一起来。

**R**

这两个部分做完以后，我对 Vue 组件通信、渲染机制和工程化封装的理解明显更深了，也让整个项目从“组件集合”变成了“有框架感的组件库”。

### 7.13 这个项目有哪些不足？如果继续迭代你会怎么做？

**S**

虽然项目已经完成了组件库的主流程，但我在梳理代码时也看到一些还能继续优化的地方。

**T**

如果把它继续往更成熟的方向推进，我希望解决性能、可访问性和发布体验这三个方面的问题。

**A**

第一，按需加载和样式拆分还可以做得更细，现在整库样式统一从 `src/styles/index.css` 引入；第二，部分组件的键盘可访问性和 ARIA 支持还可以加强；第三，RAG 服务每次问答都会重新构建知识块，后面可以做缓存或启动时预加载；第四，Select 目前更偏单选场景，多选、虚拟滚动、远程请求取消这些能力还可以继续补；第五，可以增加 CI，把测试和构建接进自动化流程。

**R**

这些不足反而让我更清楚一个组件库从“能用”到“成熟”之间还需要哪些工程化动作，面试时我也会把它当成自己的复盘点，而不是回避。

### 7.14 如果面试官问“这个项目最能体现你什么能力”，你怎么答？

**S**

组件库项目和业务项目不同，它更容易暴露一个人对前端基础和抽象能力的真实水平。

**T**

我希望让面试官看到的不只是我会写页面，而是我能把前端能力拆成组件、文档、测试和工程化交付。

**A**

我会重点讲三个点：第一，我能把复杂交互抽象成可复用组件，比如 Form、Select、Dialog、Message；第二，我能把功能和工程结合起来，比如类型输出、统一导出、测试覆盖、文档演示；第三，我愿意在项目里做额外增强，比如给文档站接 RAG，而不是停留在最低完成度。

**R**

这能让项目从“会写组件”升级成“具备前端工程意识”，我觉得这也是实习岗位比较看重的成长潜力。

## 8. 可以主动引导面试官追问的点

如果面试官让你自由展开，优先讲下面几个点：

- `Form/FormItem/Input` 的三级联动。
- `Tooltip -> Dropdown -> Select` 的能力复用。
- `Message/MessageBox` 的函数式调用实现。
- `Dialog` 的拖拽、锁滚动和关闭策略。
- 文档站 AI Assistant 的 RAG 流程。

## 9. 可能的追问与简短答法

### 9.1 你为什么不用 Element Plus，反而自己造组件？

我不是为了重复造轮子，而是为了系统理解组件库是怎么设计出来的。直接用现成库我能完成业务，但不一定能真正理解 props 设计、状态同步、组件通信、函数式调用和工程化导出的细节。

### 9.2 你在这个项目里更偏“写样式”还是“写逻辑”？

我觉得更偏逻辑和工程。样式当然也写了，但真正有含金量的是 Form 校验、浮层复用、动态挂载、统一导出、测试和文档问答这些部分。

### 9.3 你有没有考虑过可维护性？

有，我在目录结构上尽量让每个组件把模板、样式、类型、导出入口分开；复杂组件通过 hooks、types、context key 做拆分；而且通过测试和文档 demo 降低后续改动风险。

### 9.4 你怎么证明这个项目不是只会“抄”？

我会直接讲具体实现细节，比如 Form 的字段注册机制、Message 的实例堆叠、Select 的过滤策略、Dialog 的拖拽实现和 RAG 的检索流程。这些细节如果不是自己真正看过和做过，很难连续回答下来。

## 10. 面试时要诚实讲的风险点

这部分不要回避，反而会加分。

- 这是组件库项目，不是复杂业务系统，所以业务协作和真实线上场景覆盖有限。
- 部分组件还可以继续增强，比如 Select 多选、虚拟滚动、请求取消。
- AI 问答服务目前更偏“项目增强模块”，还不是高并发生产级服务。
- 自动化流程还有提升空间，比如可以补 CI、发布流程、覆盖率统计。

## 11. 项目里的真实代码锚点

面试前可以重点再看一遍这些文件：

- 统一导出入口：`src/index.ts`
- 库模式构建：`vite.config.ts`
- 类型声明输出：`tsconfig.build.json`
- 表单上下文：`src/components/Form/Form.vue`
- 表单项校验：`src/components/Form/FormItem.vue`
- 输入框联动：`src/components/Input/Input.vue`
- 浮层能力：`src/components/Tooltip/Tooltip.vue`
- 下拉菜单：`src/components/Dropdown/Dropdown.vue`
- 选择器：`src/components/Select/Select.vue`
- 对话框：`src/components/Dialog/Dialog.vue`
- 消息组件：`src/components/Message/method.ts`
- 消息盒子：`src/components/MessageBox/MessageBox.ts`
- 文档站主题增强：`docs/.vitepress/theme/index.ts`
- AI 助手前端：`docs/.vitepress/theme/components/AiAssistant.vue`
- RAG 主流程：`server/src/services/rag.ts`
- 知识切片：`server/src/services/knowledge.ts`
- 向量检索：`server/src/services/qdrant.ts`
- 测试：`src/components/BasicComponents.test.ts`
- 测试：`src/components/InteractiveComponents.test.ts`
- 测试：`src/components/FormAndInput.test.ts`

## 12. 简历写法模板

### 12.1 一行版

基于 Vue3 + TypeScript + Vite 独立实现轻量组件库 TinyElement，完成 17+ 组件文档与示例、库模式打包、类型声明输出、Vitest 测试覆盖，并为 VitePress 文档站扩展 RAG 问答助手。

### 12.2 两行版

负责从 0 到 1 搭建 Vue3 组件库工程，设计并实现 Form、Select、Dialog、Tooltip、Message 等组件，支持全量注册、类型导出和文档演示。  
使用 Vitest + Vue Test Utils 建立基础测试体系，并基于 Node.js、Qdrant 和 OpenAI-compatible API 为文档站增加 AI 检索问答能力。

## 13. 面试前最后一天复习清单

- 把 `src/index.ts` 的导出逻辑讲顺。
- 把 `Form -> FormItem -> Input` 的调用链讲顺。
- 把 `Tooltip -> Dropdown -> Select` 的复用关系讲顺。
- 把 `Message` 和 `MessageBox` 的函数式调用讲顺。
- 把 `Dialog` 的拖拽和锁滚动讲顺。
- 把 RAG 的“知识切片 -> embedding -> Qdrant 检索 -> LLM 生成”讲顺。
- 记住项目不是业务系统，要主动把亮点放在组件抽象和工程化上。
- 不要虚构性能数据，没有量化就说“提升了可维护性/复用性/交付完整度”。

## 14. 一句话收尾模板

如果面试官最后问“你觉得这个项目最有价值的地方是什么”，可以这样答：

> 我觉得这个项目最有价值的地方，是它让我把前端能力从“会写页面”推进到“能做组件抽象、工程化组织、测试验证和完整交付”，这对我申请前端实习岗位来说非常有代表性。
