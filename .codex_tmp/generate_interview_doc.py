from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "TinyElement_技术栈与面试闭环.docx"


def x(text: object) -> str:
    return escape(str(text), quote=False)


def run_text(text: object, bold: bool = False, color: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t>{x(text)}</w:t></w:r>"


def para(
    text: str = "",
    style: str = "Normal",
    *,
    bold: bool = False,
    color: str | None = None,
    align: str | None = None,
    spacing_after: int | None = None,
    keep_next: bool = False,
) -> str:
    ppr = [f'<w:pStyle w:val="{style}"/>'] if style != "Normal" else []
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if spacing_after is not None:
        ppr.append(f'<w:spacing w:after="{spacing_after}"/>')
    if keep_next:
        ppr.append("<w:keepNext/>")
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    parts = []
    for index, line in enumerate(text.split("\n")):
        if index:
            parts.append("<w:r><w:br/></w:r>")
        parts.append(run_text(line, bold=bold, color=color))
    return f"<w:p>{ppr_xml}{''.join(parts)}</w:p>"


def bullet(text: str, level: int = 0) -> str:
    indent = 360 + level * 360
    return (
        "<w:p><w:pPr>"
        '<w:pStyle w:val="ListParagraph"/>'
        f'<w:ind w:left="{indent}" w:hanging="240"/>'
        "</w:pPr>"
        f"{run_text('• ')}{run_text(text)}"
        "</w:p>"
    )


def code_para(text: str) -> str:
    return para(text, "Code")


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def cell(text: str, *, header: bool = False, width: int | None = None) -> str:
    shd = '<w:shd w:fill="EAF1FF"/>' if header else ""
    tcw = f'<w:tcW w:w="{width}" w:type="dxa"/>' if width else ""
    v_align = '<w:vAlign w:val="center"/>'
    body = "".join(para(line, "TableText") for line in str(text).split("\n"))
    return f"<w:tc><w:tcPr>{tcw}{shd}{v_align}</w:tcPr>{body}</w:tc>"


def table(headers: list[str], rows: list[list[str]], widths: list[int] | None = None) -> str:
    widths = widths or [2500] * len(headers)
    border = (
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="C9D7F2"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="C9D7F2"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="C9D7F2"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="C9D7F2"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="DCE6FA"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="DCE6FA"/>'
        '</w:tblBorders>'
    )
    margin = (
        '<w:tblCellMar>'
        '<w:top w:w="120" w:type="dxa"/>'
        '<w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="120" w:type="dxa"/>'
        '<w:right w:w="120" w:type="dxa"/>'
        '</w:tblCellMar>'
    )
    xml = [
        "<w:tbl>",
        "<w:tblPr>",
        '<w:tblW w:w="0" w:type="auto"/>',
        '<w:tblLook w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>',
        border,
        margin,
        "</w:tblPr>",
        "<w:tr>",
        "".join(cell(h, header=True, width=widths[i]) for i, h in enumerate(headers)),
        "</w:tr>",
    ]
    for row in rows:
        xml.append("<w:tr>")
        xml.append("".join(cell(row[i], width=widths[i]) for i in range(len(headers))))
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    xml.append(para("", spacing_after=160))
    return "".join(xml)


def callout(title: str, body: str) -> str:
    return table(["面试闭环提醒"], [[f"{title}\n{body}"]], widths=[9000])


def section(title: str) -> str:
    return para(title, "Heading1", keep_next=True)


def subsection(title: str) -> str:
    return para(title, "Heading2", keep_next=True)


def topic(title: str) -> str:
    return para(title, "Heading3", keep_next=True)


def interview_loop(question: str, answer: str, follow: str, trap: str = "") -> str:
    rows = [
        ["高频问法", question],
        ["回答闭环", answer],
        ["可能追问", follow],
    ]
    if trap:
        rows.append(["常见误区", trap])
    return table(["环节", "内容"], rows, widths=[1700, 7300])


tech_rows = [
    ["Vue 3", "组件开发核心框架", "Composition API、ref/reactive/computed/watch、defineProps/defineEmits/defineExpose、Transition。"],
    ["TypeScript", "公共 API 契约", "props/emits/实例暴露/表单规则/服务型组件上下文均有类型定义，tsconfig strict 开启。"],
    ["Vite 5", "开发与库模式构建", "普通 dev 模式服务本地演示，lib 模式输出 ESM/UMD，Rollup external 排除 Vue。"],
    ["VitePress", "组件文档站", "docs/components 写文档，docs/demo 写示例，@vitepress-demo-preview 嵌入 demo。"],
    ["Vue Router", "本地组件演示页", "src/views + src/router 使用 hash 路由和动态 import。"],
    ["Vitest + Vue Test Utils + jsdom", "组件测试", "覆盖基础渲染、交互、Form 校验、Tooltip Popper mock。"],
    ["async-validator", "表单校验引擎", "FormItem 按 trigger 过滤规则，并把当前字段交给 AsyncValidator 校验。"],
    ["@popperjs/core", "弹层定位", "Tooltip 创建 Popper 实例；Dropdown/Select 复用 Tooltip。"],
    ["Font Awesome", "图标体系", "Icon 组件做适配层，main.ts 与 VitePress theme 注册 fas 图标集。"],
    ["lodash-es", "工具函数", "omit/isNil/isFunction/debounce 等；lodash 与 lodash-es 同时存在，后续可收敛。"],
    ["CSS Variables + PostCSS Nested + Sass", "样式系统", "variable.css 定义 token，组件 style.css 集中导入，DatePicker 使用 scoped scss。"],
    ["Express + SSE", "AI 文档助手服务", "server/src/app.ts 作为 API-key-safe 代理，流式转发 OpenAI-compatible/Qwen 响应。"],
    ["Markdown-it + highlight.js", "AI 回答渲染", "AiAssistant.vue 禁用 HTML、支持代码高亮、打字机输出与本地持久化。"],
    ["Qdrant/RAG 原型", "知识库方向探索", "server/src/services 保留向量检索原型，但当前 tsconfig 未纳入编译，和 app.ts 的 SSE 代理不是同一条主链路。"],
]


component_rows = [
    ["基础展示", "Button、ButtonGroup、Icon、Link、Alert、Container", "统一样式、slot、props 类型、原生语义适配。"],
    ["数据录入", "Input、Switch、Rate、Select、DatePicker、Form/FormItem", "v-model、受控状态、校验、过滤、字段注册。"],
    ["反馈弹层", "Tooltip、Dropdown、Dialog、Message、MessageBox", "Popper 定位、点击外部、z-index、函数式调用、动态挂载。"],
    ["组合协作", "Collapse/CollapseItem、Container 子组件、Form 三件套", "provide/inject、父组件维护上下文、子组件注册/消费能力。"],
    ["内部工具", "RenderVnode、useClickOutside、useEventListener、useZIndex", "支撑 VNode 渲染、事件生命周期、层级管理。"],
]


quality_rows = [
    ["类型检查", "通过", "执行 npx --no-install vue-tsc --noEmit，无错误输出。"],
    ["Vitest", "25 个用例通过，但任务整体失败", "src/components/Select/Select.test.ts 是空文件，Vitest 报 No test suite found。"],
    ["测试覆盖", "有基础但不完整", "Button、Tooltip、Form/Input、基础组件、交互组件有覆盖；Select 单独测试文件待补。"],
    ["文档站", "功能结构完整，局部 Markdown 需要校验", "部分 preview/frontmatter 字符串存在引号不闭合迹象，建议 docs:build 纳入 CI。"],
    ["服务端", "SSE 代理可编译主链路；RAG 原型未纳入编译", "server/tsconfig.json 只 include app/config/types，services 目录目前不是交付主链路。"],
]


def build_body() -> str:
    parts: list[str] = []

    parts.append(para("TinyElement 技术栈与面试闭环文档", "Title", align="center"))
    parts.append(para("基于 d:\\desktop\\Web\\element-ui-main\\element-ui-main 项目源码梳理", "Subtitle", align="center"))
    parts.append(para("生成日期：2026-05-08", "Subtitle", align="center"))
    parts.append(para("定位：Vue 3 + TypeScript 组件库项目，灵感来自 Element Plus，目标是把组件实现、文档、测试、构建和面试表达串成闭环。", "Quote"))
    parts.append(page_break())

    parts.append(section("1. 项目全景"))
    parts.append(para("这个项目不是单纯页面 demo，而是一个轻量级组件库工程：src/components 提供组件实现，src/index.ts 组织库入口，docs 提供 VitePress 文档站，src/views 提供本地演示页，server 提供文档问答服务端。面试时要先讲清楚它的真实边界：它没有使用 Pinia，也不是完整业务系统；它的价值在于组件抽象、类型契约、工程化交付和复杂组件设计。"))
    parts.append(table(["模块", "主要文件", "职责"], [
        ["组件源码", "src/components/*", "按组件目录组织 .vue、types.ts、style.css、index.ts，体现组件库结构。"],
        ["统一入口", "src/index.ts", "收集组件、挂 install、导出类型、引入统一样式。"],
        ["样式系统", "src/styles/index.css / variable.css", "CSS token、reset、组件样式集中导入。"],
        ["本地演示", "src/router / src/views", "使用 Vue Router 动态导入组件演示页。"],
        ["文档站", "docs/.vitepress / docs/components / docs/demo", "VitePress + demo-preview 展示组件文档与示例。"],
        ["AI 助手前端", "docs/.vitepress/theme/components/AiAssistant.vue", "采集当前文档上下文、SSE 流式渲染、Markdown 高亮、虚拟列表。"],
        ["AI 助手服务", "server/src/app.ts", "Express 代理 OpenAI-compatible/Qwen API，保护私钥并输出 SSE。"],
        ["测试", "src/components/*.test.ts", "Vitest + Vue Test Utils + jsdom 验证组件行为。"],
        ["构建配置", "vite.config.ts / tsconfig.build.json / package.json", "库模式构建、Vue external、类型声明输出、exports 定义。"],
    ], widths=[1800, 3000, 4200]))
    parts.append(callout("项目介绍口径", "我做的是一个偏工程化的 Vue 3 组件库，覆盖组件源码、统一导出、文档示例、测试验证、库模式打包和 AI 文档问答。它的重点不是业务复杂度，而是组件抽象能力和前端工程交付能力。"))

    parts.append(section("2. 技术栈总览"))
    parts.append(table(["技术栈", "在项目中的角色", "面试可展开点"], tech_rows, widths=[1800, 2300, 4900]))
    parts.append(para("注意：package.json 里存在 @floating-ui/vue，但当前弹层实现主要使用 @popperjs/core；lodash 与 lodash-es 同时存在，实际源码更偏向 lodash-es。这类细节面试中要如实说明，体现工程判断，而不是把依赖表背成项目经验。"))

    parts.append(section("3. 组件库架构设计"))
    parts.append(subsection("3.1 组件分层"))
    parts.append(table(["类别", "代表组件", "设计重点"], component_rows, widths=[1600, 3300, 4100]))
    parts.append(subsection("3.2 统一安装与按需导出"))
    parts.append(para("src/index.ts 里把普通 SFC 包装成带 install 的插件，并把组件数组统一交给 installer.install(app)。这样既支持 app.use(TinyElement) 全量注册，也支持 import { Button, Form } 的单组件导入。面试要强调：组件库不是写完 .vue 就结束，还要考虑对外 API、类型导出、样式入口和包产物结构。"))
    parts.append(code_para("package.json exports: { \".\": { types/import/require }, \"./style.css\": \"./dist/style.css\" }"))
    parts.append(subsection("3.3 类型设计"))
    parts.append(para("项目中同时使用两类类型声明方式：Button 使用运行时 props 对象 + PropType，Alert/Input/Select/Dialog 等使用 interface + defineProps 泛型。前者更贴近 Vue 的运行时校验，后者更简洁、适合复杂 TS 接口。一个成熟回答要说明取舍：库组件对公共 API 的约束应尽量稳定，内部实现可以根据复杂度选择更适合的写法。"))
    parts.append(interview_loop(
        "为什么组件库里要显式导出 props/emits/实例类型？",
        "因为组件库面向外部使用者，类型就是 API 文档的一部分。这个项目在 src/index.ts 统一 export * from './components/*/types'，让使用者既能拿组件，也能拿到 ButtonType、DialogInstance、FormRules 等类型。",
        "如果要支持 Volar 更好的 props/slots/expose 提示，你会怎么补？",
        "只说 TypeScript 能防 bug，但说不出公共 API 契约、声明文件生成和 IDE 体验。"
    ))

    parts.append(section("4. 代表性组件闭环"))
    parts.append(subsection("4.1 Form / FormItem / Input：跨组件协作"))
    parts.append(para("Form 是这个项目最适合讲架构的组件之一。Form 通过 provide 提供 model、rules、addField、removeField、validate、resetFields、clearValidate；FormItem 注入 Form 上下文，按 prop 找字段值和规则，并把自己注册到 Form 的 fields 数组；Input 再注入 FormItem 上下文，在 input/change/blur 时调用 validate(trigger)。"))
    parts.append(interview_loop(
        "为什么 Form 不用 props 一层层传，而用 provide/inject？",
        "Form、FormItem、Input 是多层协作关系。Form 需要统一管理字段，FormItem 需要拿 model/rules，Input 需要触发当前字段校验。provide/inject 能把上下文能力下发给后代，避免中间层透传，也更接近 Element Plus 的设计。",
        "provide/inject 会不会失去响应式？InjectionKey 的价值是什么？resetFields 怎样处理初始值？",
        "只回答“方便传值”，没有讲父级字段注册、子级消费能力、类型安全和生命周期注销。"
    ))
    parts.append(bullet("async-validator 的使用闭环：根据 trigger 过滤规则 -> 去掉 trigger 字段 -> new AsyncValidator({ [prop]: rules }) -> validate 当前字段 -> 更新 validateStatus。"))
    parts.append(bullet("可优化点：FormItem.resetField 当前判断 model[prop] 为真才重置，空字符串、0、false 这类合法值可能被跳过；Input.clearInput 目前没有触发 clear 事件。"))

    parts.append(subsection("4.2 Tooltip / Dropdown / Select：弹层与组合复用"))
    parts.append(para("Tooltip 是弹层能力的底座：根据 trigger 绑定 hover/click 事件，使用 debounce 处理开关延迟，打开后在 flush: 'post' 的 watch 中创建 Popper 实例。Dropdown 复用 Tooltip 的 content slot 和 expose 的 show/hide；Select 又复用 Tooltip + Input，增加 options、过滤、远程搜索、清空和 RenderVnode 自定义 label。"))
    parts.append(interview_loop(
        "为什么 Select 不自己写定位，而复用 Tooltip？",
        "Select 的下拉面板本质也是一个受控弹层，复用 Tooltip 可以共享 Popper 定位、点击外部关闭、manual 控制和 show/hide 暴露能力。这样复杂组件是在基础能力上组合出来的，而不是重复造一套弹层。",
        "Popper 为什么要在 DOM 更新后创建？sameWidth modifier 做了什么？远程搜索为什么要 debounce？",
        "把 Select 只讲成 v-for 渲染选项，忽略弹层、输入框、过滤、状态同步和可扩展渲染。"
    ))
    parts.append(bullet("性能点：Select 当前对所有 options 直接渲染；如果选项上千，应增加虚拟列表、远程分页或懒渲染。"))
    parts.append(bullet("工程点：Tooltip defineOptions name 为 elTooltip，小写命名和导出名 ElTooltip 不完全一致，后续可统一组件 name。"))

    parts.append(subsection("4.3 Message / MessageBox / Dialog：服务型与弹窗型组件"))
    parts.append(para("Message 是函数式服务组件：method.ts 使用 h 创建 VNode，用 render 挂载到动态容器，维护 shallowReactive 的实例池，靠 id、bottomOffset 和 zIndex 管理多实例堆叠。Message.vue 只负责 UI、Transition、计时器、ESC 关闭、测量高度。MessageBox 使用 createApp 挂载组件并返回 Promise；Dialog 是声明式 v-model 弹窗，支持遮罩、ESC、锁 body 滚动、beforeClose 和拖拽。"))
    parts.append(interview_loop(
        "Message 为什么不能只写成普通模板组件？",
        "Message 的调用方式是 Message.success('保存成功')，它不属于页面结构里的固定节点，所以需要服务层动态创建、挂载、管理和销毁实例。项目里通过 h/render 创建 VNode，再由 Message.vue 暴露 visible/bottomOffset 给服务层控制。",
        "为什么用 shallowReactive 管理 instances？为什么关闭时先改 visible 再 render(null)？如何避免内存泄漏？",
        "只说“动态创建 DOM”，没有讲 Vue VNode、应用上下文、Transition、实例池和销毁链路。"
    ))
    parts.append(bullet("Dialog 当前没有使用 Teleport，而是在组件当前位置渲染遮罩和内容；成熟组件库通常会 Teleport 到 body，减少父级 overflow/z-index/transform 对弹层的影响。"))
    parts.append(bullet("MessageBox 使用 createApp 独立挂载，简单直观；若要继承全局配置/插件上下文，可参考 Message 的 appContext 传递方式。"))

    parts.append(subsection("4.4 其他组件的面试切入点"))
    parts.append(table(["组件", "可以怎么讲", "可追问点"], [
        ["Button", "props 设计、loading 行为约束、nativeType、Icon 插槽式能力、defineExpose 原生按钮 ref。", "为什么 loading 要禁用点击？为什么保留 button/submit/reset？"],
        ["Icon", "第三方图标库适配层，inheritAttrs: false 控制属性落点，color 转为 CSS 变量。", "为什么不在每个组件直接用 FontAwesomeIcon？"],
        ["Collapse", "父组件维护 activeNames，Item 通过 inject 判断 active 并触发父方法。", "手风琴模式和多展开模式的 modelValue 设计。"],
        ["Switch", "activeValue/inactiveValue 支持 string/number/boolean，role=switch。", "受控组件如何同步内部状态？键盘可访问性还要补什么？"],
        ["Rate", "useRate 抽离评分状态，v-for 渲染星星。", "为什么更成熟 API 应该用 update:modelValue/change，而不是 changeRateNums？"],
        ["DatePicker", "generateCalendar 生成 42 格日历，computed 根据日期重算。", "闰年判断应为 year % 400 === 0；isToday 里 getDay 应改为 getDate。"],
        ["Container", "根据 direction 或 slot 中 Header/Footer 推断横纵布局。", "slot VNode 类型判断的边界和动态子组件场景。"],
    ], widths=[1500, 4800, 2700]))

    parts.append(section("5. 工程化闭环"))
    parts.append(subsection("5.1 构建与包产物"))
    parts.append(para("vite.config.ts 在 mode === 'lib' 时开启库模式：entry 指向 src/index.ts，输出 tiny-element.js 和 tiny-element.umd.js，并把 vue external 掉，UMD globals 映射为 Vue。tsconfig.build.json 负责 declaration 输出到 dist/types。package.json 通过 main/module/types/exports/files 描述发布产物。"))
    parts.append(interview_loop(
        "为什么组件库要把 Vue 配成 external？",
        "Vue 是宿主项目通常已经安装的运行时，组件库如果把 Vue 打进去会造成重复依赖、包体变大，甚至出现两个 Vue 实例导致响应式/组件上下文问题。external 后由使用方提供 Vue，peerDependencies 也声明了 vue 版本。",
        "peerDependencies 和 dependencies 有什么区别？UMD globals 为什么要配？",
        "只说“减少体积”，没有讲宿主依赖、单例运行时和包格式差异。"
    ))
    parts.append(subsection("5.2 Tree-shaking 与样式副作用"))
    parts.append(para("项目支持 ESM 入口，这是 tree-shaking 的基础。但样式统一在 src/styles/index.css 导入，最终 ./style.css 作为显式样式入口导出。面试要讲清楚：JS 逻辑可以靠 ESM 静态分析裁剪，CSS 通常被视为副作用，需要在 package.json 的 sideEffects 或独立样式入口上做明确设计。"))
    parts.append(interview_loop(
        "组件库如何支持按需引入？",
        "第一层是导出单组件；第二层是 ESM 让打包器能裁剪未使用的 JS；第三层是样式策略，决定全量 style.css、组件级样式还是自动按需插件。当前项目已经有单组件导出和统一 style.css，后续可拆分每个组件样式并配置 sideEffects。",
        "sideEffects: false 能不能随便加？CSS import 会不会被摇掉？",
        "把 tree-shaking 误解成“只要 import { Button } 就一定没有其他代码”。"
    ))
    parts.append(subsection("5.3 文档与测试"))
    parts.append(table(["质量项", "当前状态", "说明"], quality_rows, widths=[1900, 2300, 4800]))
    parts.append(para("测试策略上，项目已经覆盖了基础渲染、事件触发、Popper mock、Form 校验和 Dialog 拖拽等关键行为。下一步应补齐空测试文件、Message/MessageBox 生命周期测试、Select 远程搜索测试、Dialog body scroll/ESC 测试，并把 typecheck、unit test、docs build、lib build 放进 CI。"))

    parts.append(section("6. 前端性能优化闭环"))
    parts.append(subsection("6.1 项目里已经体现的优化"))
    for item in [
        "路由演示页使用动态 import，减少初始加载压力。",
        "Tooltip 和 Select 的输入过滤使用 debounce，降低高频事件触发成本。",
        "Message 实例池使用 shallowReactive，只关心数组层级变化，避免深层代理开销。",
        "AiAssistant 消息区实现虚拟列表，只渲染可视区域和 overscan 内容。",
        "SSE 流式输出让 AI 回答边生成边展示，改善首屏反馈。",
        "Dialog/Message 的动画主要围绕 opacity/transform，通常比频繁改变 layout 属性更友好。",
    ]:
        parts.append(bullet(item))
    parts.append(subsection("6.2 可以继续优化的方向"))
    parts.append(table(["方向", "项目落点", "面试回答"], [
        ["包体积", "Font Awesome 当前导入 fas 全量图标；lodash 和 lodash-es 同时存在。", "图标按需导入、统一 lodash-es、分析 bundle，减少无用依赖。"],
        ["长列表", "Select options 全量渲染。", "大数据场景引入虚拟列表、远程分页、搜索防抖和缓存。"],
        ["弹层性能", "Tooltip 每次打开创建 Popper。", "可以懒创建并复用实例，关闭时只 hide，组件销毁时 destroy。"],
        ["布局抖动", "Message 用 getBoundingClientRect 计算高度。", "集中读写 DOM，避免循环里交替读写导致 layout thrashing。"],
        ["文档站", "VitePress + AI 助手。", "静态资源压缩、代码分割、SSE 首包、Markdown 安全渲染。"],
        ["样式", "全局 CSS 入口。", "按组件拆样式、CSS token、减少深选择器、避免无谓重排。"],
    ], widths=[1700, 3300, 4000]))
    parts.append(interview_loop(
        "你做过哪些前端性能优化？怎么和这个项目结合？",
        "我会按构建体积、运行时渲染、交互响应和网络传输四层回答。这个项目里，构建层有 ESM/UMD 和 Vue external；运行时有 computed、shallowReactive、虚拟列表；交互层有 debounce 和懒创建弹层；网络层有 SSE 流式响应。再结合可优化点，比如 FontAwesome 按需、Select 虚拟列表和 docs build 分析。",
        "如何量化？怎么判断是 JS 慢、渲染慢还是网络慢？",
        "只背懒加载、防抖、节流，没有落到项目文件和具体组件。"
    ))

    parts.append(section("7. 浏览器原理与底层原理"))
    parts.append(subsection("7.1 Vue 响应式与调度"))
    parts.append(para("可以从 ref/reactive/computed/watch/nextTick 串起来讲。FormItem 的 validateStatus 用 reactive 维护对象状态；Message 的 topOffset/bottomOffset 用 computed 依赖实例池；Tooltip 在 isOpen 变化后用 watch(..., { flush: 'post' }) 等 DOM 更新完成再创建 Popper。这背后是 Vue 的响应式依赖收集和异步更新队列。"))
    parts.append(interview_loop(
        "为什么 Tooltip 要 flush: 'post'？",
        "打开 Tooltip 后，popperNode 是 v-if 渲染出来的 DOM。如果同步创建 Popper，DOM 可能还没有挂到页面。flush: 'post' 让 watch 回调在组件 DOM 更新后执行，确保 triggerNode 和 popperNode 都可用。",
        "nextTick 和微任务有什么关系？watch flush: pre/post/sync 分别适合什么场景？",
        "只说“等 DOM 出来”，但说不出 Vue 更新队列和浏览器微任务。"
    ))
    parts.append(subsection("7.2 浏览器渲染流水线"))
    parts.append(para("浏览器通常经历 JS -> Style -> Layout -> Paint -> Composite。改变 width/top/left 更容易触发布局和绘制；transform/opacity 通常可以走合成层。Dialog 拖拽用 transform: translate(...)，Message 动画也偏 transform/opacity，这是较好的方向。反过来，频繁调用 getBoundingClientRect 会强制读取布局信息，要避免和写样式交替出现。"))
    parts.append(subsection("7.3 事件模型"))
    parts.append(para("useClickOutside 在 document 上监听 click，通过 element.contains(e.target) 判断是否点到组件外部；Dropdown/Select 内部多处使用 @click.stop 防止点击选项触发外层关闭。这里可以引出事件冒泡、捕获、stopPropagation、事件委托、全局监听清理和内存泄漏。"))
    parts.append(subsection("7.4 层叠上下文与弹层"))
    parts.append(para("useZIndex 通过模块级 ref 管理全局层级，Message 每次 nextZIndex 递增。面试要继续补充 CSS stacking context：position + z-index、transform、opacity、filter、isolation 等都会形成新的层叠上下文，这也是成熟弹层常配合 Teleport 到 body 的原因。"))
    parts.append(subsection("7.5 模块系统与 tree-shaking"))
    parts.append(para("ESM 的 import/export 是静态结构，Rollup/Vite 可以在构建期分析未使用导出；CommonJS 的 require 是运行时能力，静态分析难度更高。项目同时输出 ESM 和 UMD：ESM 面向现代打包器和 tree-shaking，UMD 面向 script 标签或兼容场景。"))
    parts.append(subsection("7.6 安全与可访问性"))
    parts.append(para("AiAssistant 使用 markdown-it 且 html: false，降低 XSS 风险；server 作为代理避免把 LLM_API_KEY 暴露到浏览器。可访问性方面，Message 有 role=alert，Switch 有 role=switch，Dialog close 按钮有 aria-label；但还可以补 aria-modal、焦点陷阱、键盘导航、aria-expanded、aria-controls、表单错误关联等。"))

    parts.append(section("8. AI 文档助手与服务端闭环"))
    parts.append(para("当前可运行主链路是：VitePress 页面采集当前 route、标题、 headings、表格、代码和正文 -> POST /api/chat -> Express 服务端拼 system prompt 并带私钥请求 OpenAI-compatible/Qwen Chat Completions -> 服务端把上游数据转成 SSE delta -> 前端 readSseStream 解析并以打字机效果渲染 Markdown。"))
    parts.append(table(["环节", "项目实现", "面试价值"], [
        ["上下文采集", "collectPageContext()", "说明能从 DOM 中抽取文档语义，控制上下文长度。"],
        ["私钥保护", "server/src/app.ts 统一加 Authorization", "API key 不进浏览器，避免泄露。"],
        ["流式协议", "text/event-stream + event/data", "用户能更快看到首段回答，适合长文本生成。"],
        ["前端消费", "ReadableStream + TextDecoder", "展示浏览器流处理、增量解析和错误超时。"],
        ["渲染安全", "markdown-it html=false", "降低 Markdown 注入 HTML 的风险。"],
        ["历史与性能", "localStorage + 虚拟列表 + ResizeObserver", "长对话时减少 DOM 节点数量，保持滚动体验。"],
    ], widths=[1700, 3600, 3700]))
    parts.append(para("另外，server/src/services 下的 rag/qdrant/embeddings/knowledge/llm 是更完整的 RAG 原型方向，但当前 server/tsconfig.json 没有 include 这些文件，config.ts 也没有暴露 qdrantUrl、embeddingModel 等字段。面试时可以说“我做过/保留了 RAG 原型设计”，但要区分当前交付主链路和待完善原型。"))

    parts.append(section("9. 高频面试题闭环题库"))
    qa = [
        ("介绍一下这个项目。",
         "先定性：Vue3 + TypeScript 轻量组件库。再讲闭环：组件源码、统一导出、文档 demo、测试、库模式构建、AI 文档助手。最后讲复杂点：Form、Tooltip/Select、Dialog/Message、SSE。",
         "你负责最复杂的是哪一块？如何证明不是普通 demo？"),
        ("Vue3 Composition API 在项目里解决了什么问题？",
         "它让逻辑按能力组织，例如 useZIndex 管层级、useClickOutside 管全局点击、useRate 管评分状态，组件内部也能把 props、state、computed、watch、expose 按职责组织。",
         "和 Options API 相比，组合式 API 在大型组件里有哪些维护优势？"),
        ("受控组件和非受控组件怎么理解？",
         "Input/Select/Switch 通过 modelValue + update:modelValue 对外受控，内部有临时状态用于展示或交互。受控的好处是父组件掌握真实值，组件只负责交互和同步。",
         "如果 props.modelValue 和内部状态不同步会怎样？"),
        ("Form 校验怎么实现？",
         "Form 提供上下文并维护字段数组，FormItem 注册自己并按 prop 拿 value/rules，Input 在事件发生时触发 FormItem.validate，整表 validate 遍历 fields 汇总错误。",
         "异步校验、多个字段联动、重置初始值怎样做？"),
        ("弹层组件最难的点是什么？",
         "定位、层级、点击外部、键盘和焦点、滚动锁定、生命周期销毁。项目里 Tooltip 用 Popper 定位，Dialog 锁滚动和 ESC，Message 用 z-index 和实例池。",
         "为什么成熟弹层常用 Teleport？如何处理焦点陷阱？"),
        ("组件库如何做按需加载？",
         "单组件导出 + ESM 静态分析 + 样式副作用策略。当前项目已有单组件导出和 style.css 入口，后续可拆组件级样式和 sideEffects 配置。",
         "CSS 会不会影响 tree-shaking？"),
        ("为什么要写测试？",
         "组件库的 API 是公共契约，测试保护 props、emits、slot、交互和生命周期行为。项目用 Vue Test Utils 挂载组件，用 jsdom 模拟 DOM，用 vi.mock 隔离 Popper。",
         "你会怎么补 Select、Message、Dialog 的测试？"),
        ("如何优化包体积？",
         "先分析 bundle。项目中可优化 FontAwesome 全量 fas、lodash/lodash-es 双依赖、样式全量导入；Vite lib external Vue 已经是正确方向。",
         "如何避免误删副作用代码？"),
        ("浏览器事件循环和 Vue nextTick 怎么结合？",
         "Vue 状态更新会批量进入异步队列，DOM 更新不是立刻完成。需要拿更新后的 DOM 时用 nextTick 或 watch flush:post，例如 Tooltip 创建 Popper。",
         "Promise 微任务、setTimeout 宏任务、requestAnimationFrame 的执行时机？"),
        ("AI 文档助手为什么需要后端？",
         "前端不能暴露 LLM_API_KEY，后端负责注入密钥、裁剪上下文、流式转发和错误处理。前端只提交问题与页面上下文，并消费 SSE。",
         "SSE 和 WebSocket 的区别？为什么这里 SSE 更合适？"),
    ]
    for q, a, f in qa:
        parts.append(interview_loop(q, a, f))

    parts.append(section("10. 简历表达"))
    parts.append(para("建议把项目写成“组件库工程化实践”，而不是“仿 Element UI 写了一些组件”。简历表达要强调可交付闭环、复杂组件、工程质量和性能/AI 扩展。"))
    for item in [
        "基于 Vue 3 + TypeScript + Vite 实现轻量组件库 TinyElement，封装 18+ 常用 UI 组件，支持全量注册、单组件导出、统一样式入口和类型声明输出。",
        "设计 Form/FormItem/Input 协作校验体系，使用 provide/inject 管理表单上下文、字段注册、async-validator 规则校验、整表 validate/reset/clearValidate。",
        "封装 Tooltip/Dropdown/Select 弹层能力，基于 Popper 实现定位，支持点击外部关闭、防抖过滤、远程搜索和 VNode 自定义渲染。",
        "实现 Message/MessageBox 函数式反馈组件，使用 h/render/createApp 动态挂载、实例池管理、z-index 分配、Transition 销毁链路和 Promise 化交互结果。",
        "搭建 VitePress 文档站与 demo 预览体系，并扩展 AI 文档问答助手，通过 Express + SSE 代理 OpenAI-compatible/Qwen 接口，实现流式 Markdown 回答。",
        "使用 Vitest + Vue Test Utils + jsdom 编写组件单测，覆盖基础渲染、交互事件、表单校验、弹层定位 mock 和 Dialog 拖拽等场景。",
    ]:
        parts.append(bullet(item))
    parts.append(callout("不要夸大的点", "不要写“完整复刻 Element Plus”“生产级无障碍完善”“完整 RAG 已上线”这类超出当前代码事实的话。更好的说法是：已完成组件库主链路，并具备继续演进到成熟组件库的架构基础。"))

    parts.append(section("11. 一周复习路线"))
    parts.append(table(["天数", "主题", "产出"], [
        ["Day 1", "项目全景、目录、入口、构建", "能 60 秒讲清项目定位和技术栈。"],
        ["Day 2", "Button/Icon/Link/Container/Alert", "能讲公共 props、slot、样式 token 和语义封装。"],
        ["Day 3", "Form/Input/Select/Switch/Rate", "能画出 Form 校验链路和受控组件模型。"],
        ["Day 4", "Tooltip/Dropdown/Dialog/Message/MessageBox", "能讲弹层定位、实例池、动态挂载、z-index、销毁链路。"],
        ["Day 5", "Vite/VitePress/测试/发布", "能回答构建产物、external、types、exports、CI。"],
        ["Day 6", "性能优化和浏览器原理", "能把 reflow、event loop、tree-shaking、SSE 落到项目代码。"],
        ["Day 7", "模拟面试", "按 STAR 讲 3 个难点：Form、Message、AI 助手，并准备追问。"],
    ], widths=[1100, 2600, 5300]))

    parts.append(section("12. 最后总结"))
    parts.append(para("这个项目的面试核心不是“我会 Vue 语法”，而是“我知道组件库为什么要这样组织”。你要把每个技术点都讲成闭环：它解决什么问题、当前项目怎么做、背后原理是什么、有什么权衡、后续怎么优化。只要能围绕 Form、Tooltip/Select、Dialog/Message、Vite 构建、VitePress 文档、AI SSE 这几条主线讲透，就能把项目从练习级 demo 讲成有工程深度的作品。"))

    return "".join(parts)


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:sz w:val="21"/><w:color w:val="1F2937"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="600" w:after="260"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="44"/><w:color w:val="163A6B"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="120"/><w:jc w:val="center"/></w:pPr><w:rPr><w:sz w:val="22"/><w:color w:val="52637A"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="360" w:after="160"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="30"/><w:color w:val="174A7C"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="25"/><w:color w:val="245B84"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="180" w:after="80"/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:b/><w:sz w:val="22"/><w:color w:val="2F6F8F"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="220" w:after="220"/><w:ind w:left="420" w:right="420"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="5D8FD6"/></w:pBdr></w:pPr><w:rPr><w:i/><w:color w:val="3F4F63"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="80"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="40" w:line="260" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="18"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="100" w:after="120"/><w:ind w:left="300"/><w:shd w:fill="F4F7FB"/></w:pPr><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Microsoft YaHei"/><w:sz w:val="18"/><w:color w:val="1F4E79"/></w:rPr></w:style>
</w:styles>"""


def document_xml() -> str:
    body = build_body()
    sect = (
        '<w:sectPr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>'
        '</w:sectPr>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>{body}{sect}</w:body>
</w:document>"""


def write_docx() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""
    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>TinyElement 技术栈与面试闭环文档</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex OOXML Builder</Application>
</Properties>"""
    settings = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/></w:settings>"""

    with ZipFile(OUT, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml())
        docx.writestr("word/_rels/document.xml.rels", doc_rels)
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/settings.xml", settings)
        docx.writestr("docProps/core.xml", core)
        docx.writestr("docProps/app.xml", app)


if __name__ == "__main__":
    write_docx()
    print(OUT)
