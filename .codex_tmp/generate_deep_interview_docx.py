from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "TinyElement_技术栈与项目深挖面试闭环.docx"


def x(value: object) -> str:
    return escape(str(value), quote=False)


def run(text: object, *, bold: bool = False, color: str | None = None, size: int | None = None) -> str:
    props: list[str] = []
    if bold:
        props.append("<w:b/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size}"/>')
    props_xml = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    text_xml = str(text).replace("\n", "\n")
    parts: list[str] = []
    for index, line in enumerate(text_xml.split("\n")):
        if index:
            parts.append("<w:br/>")
        parts.append(f"<w:t>{x(line)}</w:t>")
    return f"<w:r>{props_xml}{''.join(parts)}</w:r>"


def para(
    text: str = "",
    style: str = "Normal",
    *,
    align: str | None = None,
    keep_next: bool = False,
    spacing_before: int | None = None,
    spacing_after: int | None = None,
    color: str | None = None,
    bold: bool = False,
) -> str:
    ppr: list[str] = []
    if style != "Normal":
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    spacing: list[str] = []
    if spacing_before is not None:
        spacing.append(f'w:before="{spacing_before}"')
    if spacing_after is not None:
        spacing.append(f'w:after="{spacing_after}"')
    if spacing:
        ppr.append(f"<w:spacing {' '.join(spacing)}/>")
    if keep_next:
        ppr.append("<w:keepNext/>")
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{run(text, color=color, bold=bold)}</w:p>"


def heading(level: int, text: str) -> str:
    return para(text, f"Heading{level}", keep_next=True)


def bullet(text: str, level: int = 0) -> str:
    left = 360 + level * 360
    return (
        "<w:p><w:pPr>"
        '<w:pStyle w:val="ListParagraph"/>'
        f'<w:ind w:left="{left}" w:hanging="240"/>'
        "</w:pPr>"
        f"{run('• ')}{run(text)}"
        "</w:p>"
    )


def code(text: str) -> str:
    lines = []
    for line in text.strip("\n").split("\n"):
        lines.append(para(line, "Code", spacing_after=20))
    return "".join(lines)


def note(title: str, body: str, *, fill: str = "F4F8FF", border: str = "6B8FC9") -> str:
    return (
        "<w:tbl><w:tblPr>"
        '<w:tblW w:w="0" w:type="auto"/>'
        '<w:tblCellMar><w:top w:w="150" w:type="dxa"/><w:left w:w="180" w:type="dxa"/><w:bottom w:w="170" w:type="dxa"/><w:right w:w="180" w:type="dxa"/></w:tblCellMar>'
        f'<w:tblBorders><w:left w:val="single" w:sz="16" w:color="{border}"/><w:top w:val="single" w:sz="4" w:color="{fill}"/><w:bottom w:val="single" w:sz="4" w:color="{fill}"/><w:right w:val="single" w:sz="4" w:color="{fill}"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>'
        "</w:tblPr>"
        "<w:tr><w:tc><w:tcPr>"
        '<w:tcW w:w="9360" w:type="dxa"/>'
        f'<w:shd w:fill="{fill}"/>'
        "</w:tcPr>"
        f'{para(title, "CalloutTitle")}{para(body, "CalloutText")}'
        "</w:tc></w:tr></w:tbl>"
        + para("", spacing_after=80)
    )


def cell(text: str, *, header: bool = False, width: int | None = None, center: bool = False) -> str:
    fill = "DDEBFF" if header else "FFFFFF"
    tcw = f'<w:tcW w:w="{width}" w:type="dxa"/>' if width else ""
    align = "center" if center else None
    body = "".join(para(line, "TableHeader" if header else "TableText", align=align) for line in str(text).split("\n"))
    return (
        "<w:tc><w:tcPr>"
        f"{tcw}"
        f'<w:shd w:fill="{fill}"/>'
        '<w:vAlign w:val="center"/>'
        "</w:tcPr>"
        f"{body}"
        "</w:tc>"
    )


def table(headers: list[str], rows: list[list[str]], widths: list[int] | None = None) -> str:
    widths = widths or [int(9360 / len(headers))] * len(headers)
    out = [
        "<w:tbl><w:tblPr>",
        '<w:tblW w:w="9360" w:type="dxa"/>',
        '<w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>',
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="B8C7DC"/><w:left w:val="single" w:sz="6" w:color="B8C7DC"/><w:bottom w:val="single" w:sz="6" w:color="B8C7DC"/><w:right w:val="single" w:sz="6" w:color="B8C7DC"/><w:insideH w:val="single" w:sz="4" w:color="D7E0EC"/><w:insideV w:val="single" w:sz="4" w:color="D7E0EC"/></w:tblBorders>',
        '<w:tblLook w:firstRow="1" w:noHBand="0" w:noVBand="1"/>',
        "</w:tblPr>",
        "<w:tr><w:trPr><w:tblHeader/></w:trPr>",
    ]
    for index, header in enumerate(headers):
        out.append(cell(header, header=True, width=widths[index], center=True))
    out.append("</w:tr>")
    for row in rows:
        out.append("<w:tr>")
        for index, value in enumerate(row):
            out.append(cell(value, width=widths[index], center=False))
        out.append("</w:tr>")
    out.append("</w:tbl>")
    out.append(para("", spacing_after=120))
    return "".join(out)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


TECH_STACK_ROWS = [
    ["Vue 3 + SFC", "所有组件基于 `.vue` 单文件组件，主要使用 `<script setup>`。", "响应式原理、宏编译、组件通信、v-model、Transition。"],
    ["TypeScript", "`types.ts` 中定义 props、emits、context、instance 类型，构建时输出声明文件。", "公共 API 类型契约、PropType、ExtractPropTypes、InjectionKey、声明文件。"],
    ["Vite / Rollup", "`vite.config.ts` 区分普通应用模式与 library mode，输出 ES/UMD。", "为什么 external Vue、为什么组件库需要 ESM、tree-shaking 条件。"],
    ["VitePress", "`docs` 作为组件文档站，demo 通过插件预览。", "文档即产品、demo 与源码同步、主题增强。"],
    ["Vitest + Vue Test Utils", "覆盖 Button、Tooltip、Form、Dialog、Select 等组件行为。", "jsdom、mock 第三方库、fake timers、组件测试边界。"],
    ["async-validator", "FormItem 按 trigger 过滤规则后校验当前字段。", "schema 校验、异步校验、竞态、表单体系分层。"],
    ["Popper.js", "Tooltip 使用 createPopper，Select 复用 Tooltip 的浮层能力。", "浮层定位、滚动容器、modifier、Teleport、z-index。"],
    ["Font Awesome", "Icon 组件统一封装图标能力，入口和文档站注册图标库。", "为什么封装第三方图标、统一 API、属性透传。"],
    ["CSS Variables / CSS / SCSS", "变量集中在 `src/styles/variable.css`，组件样式集中入口导出。", "主题 token、样式按需、sideEffects、渲染性能。"],
    ["Express + SSE", "AI 文档助手服务端代理大模型并以 SSE 流式返回。", "API key 安全、跨域、流式协议、服务端职责边界。"],
    ["MarkdownIt / highlight.js / ResizeObserver", "AI 助手前端 Markdown 渲染、代码高亮、动态高度虚拟列表。", "长列表性能、流式渲染、XSS 控制、浏览器观察器。"],
]


SCENARIOS = [
    {
        "title": "场景 1：后台系统有 60 个字段，提交时要统一校验并定位第一个错误",
        "problem": "大表单字段多、校验规则复杂，用户提交失败后不知道错在哪里。",
        "solution": [
            "Form 维护字段注册表 `fields`，FormItem 在 mounted 时注册、unmounted 时注销。",
            "提交时 Form 顺序调用每个 FormItem 的 `validate`，收集错误对象。",
            "FormItem 暴露 `$el`，校验失败后可扩展 `scrollToField(prop)`，滚动到第一个错误字段。",
            "校验状态放在 FormItem，Input 只触发 `blur/change/input` 校验事件，不承担规则判断。"
        ],
        "answer": "面试时强调：这是组合组件的上下文协议设计，不是简单的表单页面逻辑。",
        "follow": "追问可能是异步校验竞态。可以用 validationId，只采纳最后一次校验结果。"
    },
    {
        "title": "场景 2：Select 远程搜索输入很快，旧请求比新请求晚回来",
        "problem": "用户输入 abc 后又输入 abcd，abc 请求慢返回，覆盖了 abcd 的结果。",
        "solution": [
            "输入触发远程搜索前先 debounce，减少请求数量。",
            "每次请求生成 requestId，响应回来时只处理最新 requestId。",
            "更完整的做法是使用 AbortController 取消上一次 fetch。",
            "loading 状态由 Select 内部管理，错误时展示空列表或错误插槽。"
        ],
        "answer": "项目已有 debounce 和 loading，可以进一步补请求竞态控制。",
        "follow": "追问防抖和节流区别：防抖等停下来再执行，节流固定间隔执行。"
    },
    {
        "title": "场景 3：Tooltip 放在 `overflow: hidden` 的表格单元格里被裁剪",
        "problem": "弹层作为当前 DOM 子节点渲染，会受父级 overflow、transform、层叠上下文影响。",
        "solution": [
            "生产级实现把弹层 Teleport 到 body。",
            "定位仍使用 Popper，把 trigger 作为 reference，把 body 下 popper 作为 floating node。",
            "配合 z-index 管理、外部点击关闭、滚动更新位置。",
            "补充焦点管理和 aria 属性，避免 Teleport 后可访问性下降。"
        ],
        "answer": "当前项目 Tooltip 能说明定位核心，但可诚实说明 Teleport 是生产级优化方向。",
        "follow": "追问 Popper modifier：offset、flip、preventOverflow、sameWidth 都属于定位管线扩展。"
    },
    {
        "title": "场景 4：Dialog 里再打开 Dialog，关闭内层时页面滚动被提前恢复",
        "problem": "多个弹窗同时锁滚动，如果每个弹窗关闭都直接恢复 body overflow，会破坏外层弹窗。",
        "solution": [
            "引入全局 scroll lock 计数器。",
            "第一个弹窗打开时记录原始 body overflow 并设置 hidden。",
            "每关闭一个弹窗计数减一，只有计数归零才恢复 overflow。",
            "Escape 和遮罩关闭也要走同一套 close 流程。"
        ],
        "answer": "项目当前 Dialog 已做 lockScroll，可以继续升级成多实例安全的 lock manager。",
        "follow": "追问为什么弹窗要锁滚动：避免背景滚动造成视觉错位和交互误触。"
    },
    {
        "title": "场景 5：接口报错瞬间产生大量 Message，页面被提示淹没",
        "problem": "多个接口失败时同时调用 Message.error，实例队列过长，影响用户判断。",
        "solution": [
            "增加 max message 数量，超过后关闭最早的提示。",
            "相同 message 和 type 做合并或节流。",
            "MessageContext 队列仍负责堆叠偏移和关闭。",
            "提供 `closeAll` 让路由切换或批量操作后清场。"
        ],
        "answer": "项目已有实例池、z-index、closeAll，可以扩展最大数量和合并策略。",
        "follow": "追问为什么用 shallowReactive：队列只关心增删，不需要深度代理 vnode/vm。"
    },
    {
        "title": "场景 6：业务方要求运行时切换主题色和暗黑模式",
        "problem": "组件库不能让用户改源码或重新打包才能换主题。",
        "solution": [
            "把颜色、字号、边框、圆角抽成 CSS Variables。",
            "浅色主题在 `:root`，暗色主题在 `.dark` 或 `[data-theme=dark]` 覆盖变量。",
            "组件样式只引用 token，不直接写死大量颜色。",
            "文档中暴露主题变量清单和覆盖示例。"
        ],
        "answer": "项目已有 `variable.css`，这是主题系统的第一步。",
        "follow": "追问 Sass 变量和 CSS 变量区别：Sass 是编译时，CSS 变量是运行时、可级联、可动态修改。"
    },
    {
        "title": "场景 7：使用者只引入 Button，但打包后整个组件库都进去了",
        "problem": "按需引入失效，包体过大。",
        "solution": [
            "确保发布 ESM 产物，并使用 named exports。",
            "每个组件提供独立入口，例如 `my-elem/button`。",
            "CSS 要声明 sideEffects，避免被误删，同时支持单组件样式入口。",
            "使用 bundle analyzer 检查 lodash、图标库等是否被全量打入。"
        ],
        "answer": "当前项目具备 named exports 和 ESM 产物，但独立入口和 sideEffects 还可完善。",
        "follow": "追问 tree-shaking 条件：ESM 静态分析、无副作用标记、构建器压缩阶段配合。"
    },
    {
        "title": "场景 8：AI 文档助手对话越来越长，页面滚动卡顿",
        "problem": "长对话如果全部渲染为 DOM，Markdown 和代码块会明显拖慢页面。",
        "solution": [
            "只渲染可视区域附近消息，使用虚拟列表。",
            "动态高度通过 ResizeObserver 记录真实高度。",
            "流式回答时只更新当前 assistant 消息，避免全量重排。",
            "历史消息持久化只保留最近 N 条，避免 localStorage 过大。"
        ],
        "answer": "项目的 AiAssistant 已经体现虚拟列表、ResizeObserver、流式渲染和本地持久化。",
        "follow": "追问动态高度虚拟列表难点：估算高度、测量回填、滚动位置补偿。"
    },
    {
        "title": "场景 9：组件库被 Nuxt/SSR 项目使用时报 `document is not defined`",
        "problem": "服务端渲染没有 window/document，组件顶层直接访问 DOM 会崩溃。",
        "solution": [
            "所有 DOM 访问放到 mounted/onMounted 或显式 `typeof window !== 'undefined'` 判断后。",
            "命令式组件 Message 只能在客户端调用。",
            "构建时不要让顶层副作用依赖浏览器对象。",
            "文档中标注 client-only 能力。"
        ],
        "answer": "项目部分组件已经有 document/window 判断，后续要系统做 SSR guard。",
        "follow": "追问为什么 SSR 没有 DOM：服务端只生成 HTML 字符串，不执行浏览器布局和事件系统。"
    },
    {
        "title": "场景 10：Tooltip 单测偶尔失败",
        "problem": "组件内部有 debounce、Transition、post flush watch，断言早于 DOM 更新。",
        "solution": [
            "Vitest 使用 fake timers 推进 debounce。",
            "状态更新后等待 nextTick，必要时等待两次以覆盖 DOM patch 和 post flush。",
            "mock Popper，不测试第三方坐标算法。",
            "afterEach 清理 timers 和 document.body。"
        ],
        "answer": "项目 Tooltip.test.ts 就是这类测试策略。",
        "follow": "追问单元测试边界：测自己的状态和调用，不测第三方库内部实现。"
    },
    {
        "title": "场景 11：DatePicker 在某些时区日期错一天",
        "problem": "使用字符串解析日期或时区转换不当，会导致本地时间偏移。",
        "solution": [
            "避免用不稳定的日期字符串解析，优先用 `new Date(year, month, day)`。",
            "内部日历计算只使用本地年月日，不混入 UTC 字符串。",
            "对跨时区业务要明确存储格式，例如后端存 ISO UTC，前端显示本地。",
            "补充月初、月末、闰年、跨年单测。"
        ],
        "answer": "项目 calendar.ts 已把日历生成逻辑抽出，适合补边界测试。",
        "follow": "追问闰年规则：能被 4 整除且不能被 100 整除，或能被 400 整除。"
    },
    {
        "title": "场景 12：Select 要支持键盘操作和无障碍访问",
        "problem": "只支持鼠标点击的 Select 对键盘用户和读屏用户不友好。",
        "solution": [
            "输入框使用 combobox/listbox 相关 aria 属性。",
            "维护 activeIndex，支持 ArrowDown/ArrowUp/Enter/Escape。",
            "选项使用 `aria-selected`，禁用项使用 `aria-disabled`。",
            "焦点不随意丢失，关闭后回到触发输入框。"
        ],
        "answer": "这是组件库从可用到成熟必须补的能力。",
        "follow": "追问 a11y 不只是加 aria，还要保证键盘路径和视觉焦点。"
    },
    {
        "title": "场景 13：Input 中文输入法下边输入边校验，用户体验很差",
        "problem": "中文拼音组合阶段会触发多次 input，如果立刻校验 required、pattern，用户还没完成输入就报错。",
        "solution": [
            "监听 compositionstart/compositionend，组合输入阶段只更新显示值，不触发强校验。",
            "compositionend 后再统一 emit input 和触发 validate。",
            "对 blur/change 校验保持原逻辑，避免提交时漏校验。",
            "测试中要模拟 composition 事件和普通 input 事件的差异。"
        ],
        "answer": "这是输入组件成熟度问题，真实中文后台系统很常见。",
        "follow": "追问 input、change、composition 事件区别，以及为什么不能只依赖 keydown。"
    },
    {
        "title": "场景 14：Form 动态增删字段后，resetFields 重置异常",
        "problem": "动态表单中字段可能被 v-if 删除或新增，如果 fields 注册表不准确，重置和校验会调用到不存在的字段。",
        "solution": [
            "FormItem mounted 时注册，unmounted 时注销，保证 fields 反映当前真实字段。",
            "初始值 initialValue 要在字段挂载时记录，并处理数组/对象的深拷贝。",
            "动态规则变化时，FormItem 要能重新读取最新 rules。",
            "resetFields 支持按 prop 局部重置，避免影响整张表单。"
        ],
        "answer": "项目已经有注册/注销机制，下一步应处理复杂值深拷贝和动态 rules。",
        "follow": "追问为什么 initialValue 不能只是引用：对象引用会被后续修改污染。"
    },
    {
        "title": "场景 15：图标库全量引入导致文档站首屏变慢",
        "problem": "Font Awesome 的全量图标集合较大，如果无差别注册 fas，可能影响首屏包体。",
        "solution": [
            "只注册项目实际使用的图标，而不是整个 fas。",
            "对文档站和组件库产物分别分析 bundle，避免文档依赖进入库包。",
            "Icon 组件保持统一 API，内部映射到可 tree-shaking 的图标集合。",
            "发布前使用 analyzer 或 size-limit 做体积门禁。"
        ],
        "answer": "项目通过 Icon 封装已经隔离了使用方式，但图标注册策略还可更细。",
        "follow": "追问为什么封装 Icon：统一 API、隔离第三方库、方便替换图标方案。"
    },
    {
        "title": "场景 16：MessageBox 独立 createApp 后拿不到主应用全局配置",
        "problem": "createApp 会创建新的应用上下文，可能拿不到主应用注册的组件、provide、全局属性或国际化配置。",
        "solution": [
            "像 Message 一样接收并传递 appContext。",
            "或者改用 h + render，并设置 vnode.appContext。",
            "对命令式组件建立统一 service factory，避免每个组件策略不一致。",
            "测试全局组件、主题变量、国际化文案在命令式弹窗中的可用性。"
        ],
        "answer": "这是命令式组件从可用到工程化一致性的关键升级点。",
        "follow": "追问 h/render/createApp 的区别，以及 appContext 包含什么。"
    },
    {
        "title": "场景 17：AI 助手回答了当前文档没有的组件 API",
        "problem": "模型容易根据通用知识补全不存在的 props/events，造成文档误导。",
        "solution": [
            "system prompt 明确要求优先当前页面上下文，不足时说明信息不足。",
            "服务端只传当前页面 API 表格、代码示例和可见文本，限制泛化空间。",
            "升级 RAG 后要求回答附带来源片段和文件路径。",
            "前端可在答案底部展示引用来源，便于用户回查。"
        ],
        "answer": "项目 app.ts 已经在 prompt 里约束不要编造 API，这是 AI 文档助手最重要的安全边界之一。",
        "follow": "追问 prompt injection：用户可能要求忽略系统提示，需要服务端固定规则和上下文白名单。"
    },
    {
        "title": "场景 18：组件库发布后用户反馈样式没有生效",
        "problem": "用户只 import 了组件 JS，没有引入 CSS，或者构建器把 CSS 当副作用摇掉。",
        "solution": [
            "文档明确要求 `import 'my-elem/style.css'`。",
            "package exports 暴露 `./style.css`。",
            "声明 `sideEffects: ['**/*.css']`，避免 CSS 被 tree-shaking 删除。",
            "更进一步提供自动样式按需插件或每个组件的 style 入口。"
        ],
        "answer": "项目已经导出 style.css，但 sideEffects 和组件级样式入口还可以补。",
        "follow": "追问 JS tree-shaking 和 CSS side effect 为什么冲突。"
    },
    {
        "title": "场景 19：Dialog 关闭后焦点丢失，键盘用户不知道回到哪里",
        "problem": "弹窗关闭后焦点没有回到打开按钮，可访问性和键盘体验都不好。",
        "solution": [
            "打开前记录 document.activeElement。",
            "Dialog 打开后把焦点移动到弹窗容器或首个可聚焦元素。",
            "Tab/Shift+Tab 限制在弹窗内部形成 focus trap。",
            "关闭后恢复到打开前元素。"
        ],
        "answer": "当前 Dialog 已有 ESC 和遮罩关闭，生产级还要补焦点管理。",
        "follow": "追问为什么弹窗需要 focus trap：避免键盘焦点跑到背景内容。"
    },
    {
        "title": "场景 20：路由切换后仍然有旧页面的全局事件监听",
        "problem": "组件销毁时没有移除 window/document 监听，会造成内存泄漏或旧逻辑误触发。",
        "solution": [
            "所有全局事件都通过 useEventListener 这类 composable 注册。",
            "onBeforeUnmount/onUnmounted 统一 remove。",
            "对弹窗、Tooltip、Select 这类高频组件重点检查。",
            "测试中 afterEach 清理 document.body，也能暴露一些泄漏问题。"
        ],
        "answer": "项目已有 useEventListener 和 useClickOutside，这正是把 DOM 副作用工程化的体现。",
        "follow": "追问内存泄漏排查：Performance Memory、事件监听面板、堆快照。"
    },
    {
        "title": "场景 21：Select 选项非常多，打开下拉瞬间卡顿",
        "problem": "一次性渲染几千个 li，会造成 DOM 创建、布局和事件绑定压力。",
        "solution": [
            "下拉面板内部做虚拟列表，只渲染可视区域选项。",
            "远程搜索时限制返回数量，并提供分页或更多加载。",
            "本地过滤用 debounce，避免每个字符都全量 filter。",
            "选项渲染支持 RenderVnode 时要注意复杂 VNode 的渲染成本。"
        ],
        "answer": "当前 Select 支持过滤和远程搜索，下一步性能升级就是虚拟选项列表。",
        "follow": "追问虚拟列表固定高度和动态高度实现差异。"
    },
    {
        "title": "场景 22：CI 中测试偶发失败，但本地稳定",
        "problem": "异步更新、定时器、动画、第三方 DOM 测量在 CI 环境更容易产生时序问题。",
        "solution": [
            "关闭不必要动画或 mock Transition。",
            "用 fake timers 控制 debounce/timeout。",
            "异步断言前明确等待 nextTick 或 flushPromises。",
            "第三方定位、ResizeObserver、IntersectionObserver 做稳定 mock。"
        ],
        "answer": "项目测试 setup 已 mock ResizeObserver，Tooltip 测试也 mock Popper 和 fake timers。",
        "follow": "追问为什么不要 sleep：固定等待慢且不稳定，应该等待明确状态。"
    },
]


QA_ROWS = [
    ["Vue 响应式", "Vue 3 响应式底层是什么？", "Proxy 拦截 get/set，读取时 track，修改时 trigger；computed 是带缓存的 effect，watch 用于副作用。", "为什么 props 改了 DOM 不立即更新？"],
    ["`<script setup>`", "`defineProps` 是运行时函数吗？", "它是编译宏，编译阶段会转成组件选项；代码里不用 import。", "宏和普通函数有什么区别？"],
    ["v-model", "Input 如何实现 v-model？", "接收 modelValue，内部维护 inputValue，输入时 emit update:modelValue，同步外部数据源。", "受控和非受控组件区别？"],
    ["provide/inject", "为什么 Form 用 provide/inject？", "字段数量和层级不确定，用上下文协议避免层层传 props，并用 InjectionKey 保证类型。", "它能替代 Pinia 吗？"],
    ["TypeScript", "PropType 和 interface 的关系？", "interface 是 TS 静态类型；PropType 把泛型类型桥接到 Vue 运行时 props 声明。", "ExtractPropTypes 有什么用？"],
    ["构建", "为什么 external Vue？", "避免把 Vue 打进组件库，减小包体，避免多 Vue 实例和响应式上下文不一致。", "peerDependencies 为什么必要？"],
    ["tree-shaking", "按需引入为什么有时失效？", "可能没有 ESM、入口副作用过多、样式副作用没声明、组件被集中注册导致全量引用。", "CSS sideEffects 怎么写？"],
    ["Popper", "为什么不用自己算 Tooltip 坐标？", "真实浮层要处理边界、滚动、翻转、偏移、箭头和层叠上下文，Popper 更可靠。", "modifier 是什么？"],
    ["Message", "命令式组件如何挂载？", "用 h 创建 VNode，render 到临时容器，关闭时改 visible 播放动画，动画后 render(null) 并移除 DOM。", "appContext 为什么重要？"],
    ["SSE", "AI 助手为什么用 SSE？", "大模型回答是服务端单向 token 流，SSE 简单、基于 HTTP、适合流式文本。", "和 WebSocket 怎么选？"],
    ["浏览器渲染", "transform 为什么适合拖拽？", "transform 通常进入合成阶段，减少布局影响；top/left 更容易触发布局。", "什么是重排/重绘/合成？"],
    ["测试", "为什么 mock Popper？", "单测应验证自己组件的调用时机和显示逻辑，不测试第三方定位算法。", "fake timers 解决什么？"],
]


def add_intro(body: list[str]) -> None:
    body.append(para("TinyElement 技术栈与项目深挖面试闭环", "Title"))
    body.append(para("Vue 3 + TypeScript 组件库项目 · 技术栈 · 底层原理 · 性能优化 · 工程化 · 浏览器原理 · 场景题方案", "Subtitle"))
    body.append(para("生成日期：2026-05-08    项目路径：D:/desktop/Web/element-ui-main/element-ui-main", "Meta", align="center"))
    body.append(note("文档定位", "这是一份用于面试准备的中文 Word 文档。它不只列技术栈，而是把每个技术点放回 TinyElement 项目：为什么用、在哪里用、怎么讲、会被怎样追问、真实业务场景下如何扩展。"))
    body.append(heading(1, "0. 面试开场：先把项目讲成一个系统"))
    body.append(para("推荐开场话术："))
    body.append(para("我做的是一个仿 Element Plus 思路的 Vue 3 + TypeScript 组件库。项目的重点不是单纯写 UI，而是从组件库工程角度设计公共 API、类型约束、全局安装、按需导出、样式 token、文档站、单元测试和库模式构建。比较能体现深度的模块包括 Form 的上下文注册和 async-validator 校验、Tooltip/Select 的浮层复用、Message/MessageBox 的命令式挂载，以及 VitePress 文档站里的 AI 问答助手。", "Quote"))
    body.append(para("面试官通常不怕你项目小，怕的是你只能描述功能。这个项目应该按“组件设计 + 工程化 + 性能 + 浏览器底层 + 真实场景”五条线来讲。"))
    body.append(page_break())


def add_stack_map(body: list[str]) -> None:
    body.append(heading(1, "1. 技术栈全景地图"))
    body.append(para("下面这张表建议先整体背熟。它能帮助你在面试中从“我用了某技术”升级成“这个技术在项目中的职责是什么”。"))
    body.append(table(["技术栈", "项目落点", "可深挖面试点"], TECH_STACK_ROWS, [1700, 3900, 3760]))
    body.append(heading(2, "1.1 项目目录与职责边界"))
    rows = [
        ["`src/components`", "组件库主体。每个组件独立维护 SFC、类型和样式。", "组件库的基本单位是“组件包”，而不是业务页面。"],
        ["`src/components/*/types.ts`", "props、emits、context、instance 类型。", "公共 API 前置，利于维护和声明文件生成。"],
        ["`src/hooks`", "useClickOutside、useEventListener、useZIndex。", "把 DOM 副作用和跨组件策略抽离。"],
        ["`src/styles`", "reset、变量、全量样式入口。", "主题 token、样式入口、按需样式扩展。"],
        ["`src/index.ts`", "全局安装、单组件导出、类型导出。", "这是组件库对使用者的 API 门面。"],
        ["`docs`", "VitePress 文档与 demo。", "组件库需要可学习、可复制、可验证的文档体验。"],
        ["`server`", "AI 文档助手服务端。", "保护 API key，负责 prompt 拼装和 SSE 流式转发。"],
    ]
    body.append(table(["目录", "职责", "面试表达"], rows, [2200, 3600, 3560]))


def add_vue_ts(body: list[str]) -> None:
    body.append(heading(1, "2. Vue 3 深挖：从项目实现讲到底层原理"))
    body.append(heading(2, "2.1 Composition API 为什么适合组件库"))
    body.append(para("组件库组件往往不是单一业务流程，而是多个可配置能力的组合。Input 同时有 v-model、清空、密码显隐、插槽、表单校验联动；Dialog 同时有显示状态、遮罩、滚动锁定、拖拽、ESC 关闭；Tooltip 同时有触发方式、延迟、防抖、Popper 定位和外部点击关闭。Composition API 可以按能力组织代码，也便于抽出 composable。"))
    body.append(note("项目落点", "Button 使用 computed 生成类名；Input 使用 watch 同步 modelValue；Form/Collapse 使用 provide/inject；Dialog 使用生命周期清理全局事件；Rate 使用 useRate 抽离评分状态。"))
    body.append(heading(3, "面试闭环"))
    body.append(bullet("解决什么问题：复杂组件内部能力多，Options API 容易按生命周期分散代码。"))
    body.append(bullet("项目怎么做：使用 ref、reactive、computed、watch、onMounted/onBeforeUnmount 按逻辑组织。"))
    body.append(bullet("底层原理：Vue 3 响应式通过 Proxy 和 effect 系统完成依赖收集与触发更新。"))
    body.append(bullet("真实场景：弹窗拖拽、Select 搜索、Form 校验都属于状态 + 副作用组合。"))
    body.append(heading(2, "2.2 响应式、computed、watch 的选择"))
    body.append(table(["能力", "项目例子", "选择原因"], [
        ["ref", "Dialog 的 visible、rendered；Input 的 inputValue。", "适合基本类型或单个 DOM 引用。"],
        ["reactive", "FormItem 的 validateStatus；Dialog 的 dragState。", "适合一组相关状态，修改字段时保持对象引用。"],
        ["computed", "Button class、FormItem isRequired、Select filteredPlaceholder。", "用于纯派生值，有缓存，无副作用。"],
        ["watch", "同步 props.modelValue、打开 Tooltip 后创建 Popper。", "用于响应变化后的副作用。"],
    ], [1600, 3600, 4160]))
    body.append(heading(2, "2.3 v-model 与受控组件"))
    body.append(para("Vue 3 默认 v-model 等价于 `:modelValue=\"value\"` 加 `@update:modelValue=\"value = $event\"`。项目中的 Input、Switch、Select、Dialog 都采用这个协议。"))
    body.append(code("""
// Input 的核心思想
const props = defineProps<{ modelValue?: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

const inputValue = ref(props.modelValue)
watch(() => props.modelValue, value => {
  inputValue.value = value
})

const handleInput = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  inputValue.value = value
  emit('update:modelValue', value)
}
"""))
    body.append(para("面试要点：props 是外部数据源，不能直接修改；内部状态只服务交互体验；所有真实值变化都要通过 emit 交还父组件。"))
    body.append(heading(2, "2.4 provide/inject 是组件库内部协议"))
    body.append(para("Form 和 Collapse 都不是简单父子组件，它们要管理一组数量不确定的子组件。Form 通过 provide 下发 model、rules 和方法，FormItem 注入后注册到 fields。Input 再注入 FormItem 上下文，触发字段校验。"))
    body.append(table(["问题", "回答"], [
        ["为什么不用 props 一层层传？", "FormItem 和 Input 之间可能隔着布局组件、插槽和自定义组件，层层传递会污染使用者模板。"],
        ["为什么 key 用 InjectionKey？", "用 Symbol 避免命名冲突，用泛型保证 inject 结果有类型。"],
        ["能不能替代 Pinia？", "不能。provide/inject 适合局部组件树协议，Pinia 适合跨页面业务状态。"],
        ["响应式会丢吗？", "如果 provide 的是响应式对象或 ref，inject 后仍能响应；如果 provide 普通值，它本身不会自动变响应式。"],
    ], [2600, 6760]))
    body.append(heading(1, "3. TypeScript 深挖：从类型约束到发布契约"))
    body.append(para("组件库中的 TypeScript 不是为了“写起来更高级”，而是为了让公共 API 可预测、可提示、可维护。"))
    body.append(heading(2, "3.1 Props / Emits / Context / Expose"))
    body.append(table(["类型设计点", "项目落点", "面试说法"], [
        ["联合类型", "ButtonType、ButtonSizeType、NativeType。", "限制使用者只能传合法枚举值。"],
        ["函数重载式 emits", "InputEmits。", "让不同事件名对应不同参数类型。"],
        ["ExtractPropTypes", "FormProps、FormItemProps。", "从运行时 props 配置反推 TS 类型，避免重复声明。"],
        ["InjectionKey", "formContextKey、formItemContextKey。", "让 provide/inject 成为有类型的上下文协议。"],
        ["Instance 类型", "TooltipInstance、DialogInstance。", "规范 defineExpose 暴露给父组件的方法。"],
    ], [1900, 3000, 4460]))
    body.append(heading(2, "3.2 声明文件为什么重要"))
    body.append(para("组件库最终被别的项目安装使用，使用者不会直接看源码。`dist/types/index.d.ts` 就是这个库对外承诺的类型契约。项目通过 `vue-tsc -p tsconfig.build.json` 输出声明文件，并在 package.json 中用 `types` 指向它。"))
    body.append(note("面试追问", "`vue-tsc` 和 `tsc` 的区别：普通 tsc 不理解 `.vue` 单文件组件里的模板和宏类型，vue-tsc 基于 Vue 编译器和 Volar 类型能力处理 Vue SFC。"))


def add_components(body: list[str]) -> None:
    body.append(heading(1, "4. 组件库架构深挖"))
    body.append(heading(2, "4.1 入口文件：全局安装 + 单组件导出"))
    body.append(para("`src/index.ts` 是组件库的门面。它通过 `withInstall` 给普通 SFC 补充 `install(app)`，让组件既能 `app.use(Button)`，也能被全量安装器统一注册。"))
    body.append(code("""
type SFCWithInstall<T> = T & Plugin
const withInstall = <T extends { name: string }>(component: T) => {
  const target = component as SFCWithInstall<T>
  target.install = (app: App) => {
    app.component(target.name, target)
  }
  return target
}
"""))
    body.append(para("Message 这类命令式组件不只是模板组件，所以要挂到 `app.config.globalProperties.$message`；MessageBox 返回 Promise，也更像服务式 API。"))
    body.append(heading(2, "4.2 样式系统：token、全量入口与按需扩展"))
    body.append(para("项目使用 CSS Variables 定义颜色、字号、边框、圆角和动画时长。变量集中在 `src/styles/variable.css`，组件样式通过 `src/styles/index.css` 汇总。"))
    body.append(table(["设计点", "当前实现", "可升级方向"], [
        ["主题 token", "使用 `--el-color-primary` 等 CSS 变量。", "支持 dark class、品牌主题包、运行时切换。"],
        ["样式入口", "统一 `style.css` 入口。", "增加组件级样式入口，如 `button/style.css`。"],
        ["tree-shaking", "JS 有 named exports。", "在 package.json 声明 CSS sideEffects，防止样式被摇掉。"],
        ["样式隔离", "组件类名以 `el-` 前缀组织。", "可继续引入 BEM 规范、CSS layer、命名空间配置。"],
    ], [1700, 3300, 4360]))
    body.append(heading(2, "4.3 Form 体系：最值得重点讲的组件"))
    body.append(para("Form 是组件库面试里最能体现架构意识的模块，因为它同时包含上下文通信、字段注册、异步校验、状态管理、方法暴露和输入控件联动。"))
    body.append(table(["角色", "职责", "不能越界做什么"], [
        ["Form", "保存 model/rules，维护 fields 注册表，统一 validate/reset/clear。", "不关心具体输入控件怎么渲染。"],
        ["FormItem", "根据 prop 读取字段值，筛选 trigger 规则，执行 async-validator，维护错误状态。", "不直接修改复杂业务流程，只处理字段级逻辑。"],
        ["Input/Select", "负责用户输入、触发 update:modelValue，并通知 FormItem 校验。", "不理解整张表单的规则结构。"],
    ], [1600, 4300, 3460]))
    body.append(heading(2, "4.4 Tooltip / Select / Dropdown：浮层复用体系"))
    body.append(para("Tooltip 是底层浮层能力，Select 和 Dropdown 不应该重复实现定位、外部点击、显示隐藏和触发控制。项目里 Select 通过 Tooltip 的 manual 模式手动控制下拉面板，这是组件复用思维。"))
    body.append(note("可优化点", "生产级浮层通常需要 Teleport 到 body、焦点管理、键盘导航、aria 属性、滚动更新位置和嵌套弹层处理。当前实现已经能讲清核心，但要诚实说明这些升级方向。", fill="FFF8E8", border="D79B22"))
    body.append(heading(2, "4.5 Dialog / Message / MessageBox：反馈组件体系"))
    body.append(table(["组件", "使用方式", "核心实现", "面试价值"], [
        ["Dialog", "模板声明 + v-model 控制。", "Transition、visible/rendered、锁滚动、ESC、遮罩、拖拽。", "弹窗状态机和 DOM 副作用管理。"],
        ["Message", "命令式函数调用。", "`h + render` 动态挂载，实例队列，z-index，关闭销毁。", "Vue 底层渲染 API 和服务式组件。"],
        ["MessageBox", "命令式函数 + Promise。", "`createApp` 动态挂载，用户动作 resolve。", "异步交互建模和命令式 API 设计。"],
    ], [1500, 1900, 3600, 2360]))


def add_engineering(body: list[str]) -> None:
    body.append(heading(1, "5. 工程化深挖：Vite、构建、发布、文档、测试"))
    body.append(heading(2, "5.1 Vite 开发模式和库模式"))
    body.append(para("项目在普通开发时是 Vite 应用；在 `--mode lib` 时切换到库模式构建，入口是 `src/index.ts`，输出 ES 和 UMD 两种格式。Vue 被 external，不打进组件库产物。"))
    body.append(table(["配置点", "原因", "面试追问"], [
        ["`build.lib.entry`", "组件库以 `src/index.ts` 作为公共入口。", "为什么入口不能是 main.ts？"],
        ["`formats: ['es', 'umd']`", "ES 给现代构建器，UMD 给 script 或兼容场景。", "ESM/CJS/UMD 区别？"],
        ["`external: ['vue']`", "避免重复打包 Vue，交给宿主项目提供。", "peerDependencies 作用？"],
        ["`vue-tsc`", "构建前类型检查或生成声明文件。", "为什么 tsc 不够？"],
    ], [2300, 3800, 3260]))
    body.append(heading(2, "5.2 package.json 发布字段"))
    body.append(para("面试官问 package.json，不要只说脚本。组件库最关键的是使用者如何解析你的包。"))
    body.append(table(["字段", "含义", "本项目表达"], [
        ["main", "传统 CommonJS/UMD 入口。", "`dist/tiny-element.umd.js`。"],
        ["module", "ESM 入口，利于 tree-shaking。", "`dist/tiny-element.js`。"],
        ["types", "TypeScript 类型入口。", "`dist/types/index.d.ts`。"],
        ["exports", "明确允许使用者导入的路径。", "暴露根入口和 `./style.css`。"],
        ["peerDependencies", "宿主必须提供的依赖。", "Vue 应该由使用项目安装。"],
    ], [1700, 3600, 4060]))
    body.append(heading(2, "5.3 VitePress 文档站"))
    body.append(para("组件库文档站不仅是说明书，也是质量保障。demo 与真实组件一起运行，能逼着组件 API 稳定，也方便面试展示。项目通过 VitePress sidebar 管理组件分类，通过 demo preview 插件展示可运行示例，并在主题层挂载 AI 助手。"))
    body.append(heading(2, "5.4 测试策略"))
    body.append(para("组件库测试重点是公共 API 稳定，不是把实现细节全部锁死。项目使用 Vitest + Vue Test Utils + jsdom，测试 props、emits、插槽、命令式方法、表单校验、弹层显示和定时器逻辑。"))
    body.append(table(["测试对象", "项目测试方式", "为什么这样测"], [
        ["Button", "检查 class、disabled、icon、loading。", "基础组件重点测 props 到 DOM 的映射。"],
        ["Tooltip", "mock Popper，fake timers 推进 debounce。", "第三方定位算法不属于本项目单测范围。"],
        ["Form + Input", "调用 validate，验证 reject/resolve。", "表单体系重点测跨组件协作。"],
        ["Dialog", "模拟拖拽和关闭。", "弹窗组件重点测事件和副作用。"],
        ["Select", "选择、清空、过滤。", "复合输入组件重点测状态同步。"],
    ], [1800, 3400, 4160]))


def add_performance_browser(body: list[str]) -> None:
    body.append(heading(1, "6. 性能优化：从项目现状到真实业务方案"))
    body.append(heading(2, "6.1 运行时性能"))
    body.append(table(["优化点", "项目落点", "可扩展方案"], [
        ["防抖", "Select 远程搜索使用 debounce。", "增加请求取消和响应顺序控制。"],
        ["浅响应式", "Message 实例队列使用 shallowReactive。", "只追踪队列增删，不代理复杂 vnode/vm。"],
        ["虚拟列表", "AI 助手只渲染可视消息。", "动态高度测量、滚动补偿、overscan。"],
        ["事件清理", "useEventListener / useClickOutside 卸载时 remove。", "统一管理全局事件，避免内存泄漏。"],
        ["合成动画", "Dialog 拖拽使用 transform。", "优先 transform/opacity，减少 layout 影响。"],
    ], [1900, 3500, 3960]))
    body.append(heading(2, "6.2 构建和包体性能"))
    body.append(bullet("Vue external：减少包体，避免重复 Vue 实例。"))
    body.append(bullet("lodash-es：ESM 形式更利于 tree-shaking，但仍要避免全量导入。"))
    body.append(bullet("路由 demo 动态 import：演示页按路由拆分，减少首屏加载。"))
    body.append(bullet("可升级：独立组件入口、独立样式入口、sideEffects、bundle analyzer、size limit。"))
    body.append(heading(2, "6.3 浏览器渲染原理"))
    body.append(para("从浏览器角度看，性能优化可以归结为少做 JS、少做样式计算、少做布局、少绘制、少传输。组件库尤其要关注弹层测量、拖拽动画、长列表和频繁输入。"))
    body.append(table(["概念", "解释", "项目关联"], [
        ["重排 Layout", "元素几何信息变化后重新计算布局。", "Popper 测量 reference/popper 尺寸时需要布局信息。"],
        ["重绘 Paint", "颜色、阴影、背景变化后重新绘制。", "主题色变化、hover、错误状态样式会触发。"],
        ["合成 Composite", "浏览器把图层进行 transform/opacity 合成。", "Dialog 拖拽用 transform 更适合高频移动。"],
        ["事件循环", "宏任务、微任务、渲染更新共同调度。", "nextTick 等待 Vue DOM patch 后再测量或滚动。"],
    ], [1600, 3900, 3860]))
    body.append(heading(1, "7. 浏览器原理与前端底层题"))
    body.append(heading(2, "7.1 事件循环与 nextTick"))
    body.append(para("Vue 状态变化不是立即同步更新 DOM，而是进入调度队列批量更新。`nextTick` 用于等待 DOM patch 完成。Tooltip 测量弹层位置、AI 助手滚动到底部，都需要在 DOM 更新后执行。"))
    body.append(heading(2, "7.2 事件传播与外部点击关闭"))
    body.append(para("useClickOutside 在 document 监听 click，再通过 `element.contains(event.target)` 判断是否点在组件外部。Select 内部选项点击使用 stop，Dialog 遮罩点击用 `target === currentTarget` 区分点击遮罩还是内容。"))
    body.append(heading(2, "7.3 CORS、代理和服务端安全"))
    body.append(para("AI 服务不能把 API key 放到浏览器。项目通过 Express 服务读取 `.env`，前端只请求 `/api/chat`。VitePress dev proxy 解决本地跨域和路径统一问题。服务端还能做限流、上下文裁剪、日志和错误兜底。"))
    body.append(heading(2, "7.4 XSS 与 Markdown 渲染"))
    body.append(para("AI 助手使用 MarkdownIt 渲染模型回答，配置中 `html: false`，避免直接渲染模型输出的 HTML。真实业务里还应对链接、代码块、用户输入和富文本做白名单或 sanitizer。"))


def add_scenarios(body: list[str]) -> None:
    body.append(heading(1, "8. 真实场景题与解决方案"))
    body.append(para("下面这些题更接近真实面试。建议按“问题 -> 风险 -> 方案 -> 项目落点 -> 可追问”来答。"))
    for item in SCENARIOS:
        body.append(heading(2, item["title"]))
        body.append(para("问题：" + item["problem"], "StrongPara"))
        body.append(para("解决方案："))
        for s in item["solution"]:
            body.append(bullet(s))
        body.append(para("项目回答：" + item["answer"]))
        body.append(para("可能追问：" + item["follow"], "Quote"))


def add_ai_and_bottom(body: list[str]) -> None:
    body.append(heading(1, "9. AI 文档助手：前后端链路深挖"))
    body.append(para("这个项目的 AI 助手可以作为工程化加分项，但要讲准确：当前主服务是“当前页面上下文 + 服务端代理 + SSE 流式回答”，而不是已经完整上线的 Qdrant RAG。仓库中预留了 knowledge、embedding、qdrant、rag 服务代码，可以作为扩展方向。"))
    body.append(table(["阶段", "当前实现", "可深挖点"], [
        ["前端采集上下文", "采集标题、headings、table、code、可见文本。", "如何控制上下文长度，如何避免噪声。"],
        ["服务端代理", "Express 读取 API key，请求 OpenAI-compatible/Qwen 接口。", "为什么 key 不能放前端，如何限流。"],
        ["流式返回", "SSE 发送 delta/done/error。", "SSE、WebSocket、轮询区别。"],
        ["前端渲染", "fetch reader 解析流，MarkdownIt 渲染，打字机效果。", "流式 UI、错误处理、XSS 防护。"],
        ["长对话性能", "虚拟列表 + ResizeObserver + localStorage。", "动态高度虚拟滚动。"],
        ["RAG 扩展", "预留 docs/demo/types 切片、embedding、Qdrant。", "离线索引、向量检索、重排、引用来源。"],
    ], [1600, 3900, 3860]))
    body.append(heading(2, "9.1 如果面试官问 RAG 怎么升级"))
    body.append(bullet("离线构建知识库：扫描 docs/components、docs/demo、src/components/*/types.ts。"))
    body.append(bullet("切片：按组件、章节、示例、类型定义拆 chunk，保留 filePath、route、sourceType。"))
    body.append(bullet("向量化：调用 embedding 模型，分批写入 Qdrant。"))
    body.append(bullet("检索：用户问题向量化，按 route/component/sourceType 做过滤和加权。"))
    body.append(bullet("重排：关键词、当前页面、文档优先级加分。"))
    body.append(bullet("生成：把 top-k 片段作为上下文，要求模型给出来源，避免幻觉。"))
    body.append(heading(1, "10. 高频面试题闭环速查"))
    body.append(para("这一部分建议按卡片背：先说标准答法，再主动抛出项目落点，最后准备一个追问。"))
    for direction, question, standard, follow in QA_ROWS:
        body.append(heading(3, f"{direction}：{question}"))
        body.append(bullet("标准答法：" + standard))
        body.append(bullet("项目落点：结合当前组件或配置文件举例，不要只背概念。"))
        body.append(bullet("可能追问：" + follow))
    body.append(heading(1, "11. 简历与项目讲法"))
    body.append(heading(2, "11.1 可以写进简历的亮点"))
    resume = [
        "基于 Vue 3 + TypeScript 设计并实现组件库，封装 Button、Input、Form、Select、Tooltip、Dialog、Message 等组件，支持全局安装、单组件导出和类型声明生成。",
        "设计 Form/FormItem/Input 联动校验体系，基于 provide/inject 建立表单上下文，通过 async-validator 支持字段级规则校验、触发时机过滤、重置与清空校验状态。",
        "封装 Tooltip 浮层基础能力，基于 Popper.js 支持 hover/click/manual 触发、外部点击关闭，并复用于 Select/Dropdown 等复合组件。",
        "实现 Message/MessageBox 命令式反馈组件，使用 Vue h/render/createApp 动态挂载，管理实例队列、z-index、关闭动画和 Promise 交互结果。",
        "搭建 VitePress 组件文档站和 demo 预览体系，接入文档页 AI 问答助手，基于 Express + SSE 实现流式回答和前端 Markdown 渲染。",
        "使用 Vitest + Vue Test Utils 编写组件单元测试，覆盖 props 渲染、emits、插槽优先级、表单校验、弹层交互和定时器逻辑。"
    ]
    for item in resume:
        body.append(bullet(item))
    body.append(heading(2, "11.2 不能夸大的点"))
    body.append(bullet("不要说完整复刻 Element Plus。更准确是：参考 Element Plus 思路，实现核心组件库能力。"))
    body.append(bullet("不要说已经完整实现生产级 RAG。更准确是：实现文档页上下文问答助手，并预留 RAG 检索扩展。"))
    body.append(bullet("不要说完整按需样式加载。当前是全量样式入口，后续可升级组件级样式入口和 sideEffects。"))
    body.append(heading(1, "12. 最后复习路线"))
    body.append(bullet("第一轮：读 `src/index.ts`，掌握全局安装、单组件导出、类型导出。"))
    body.append(bullet("第二轮：读 Form/FormItem/Input，掌握组件通信、字段注册、校验链路。"))
    body.append(bullet("第三轮：读 Tooltip/Select/Dialog/Message，掌握浮层、命令式组件和 DOM 副作用。"))
    body.append(bullet("第四轮：读 vite.config.ts、package.json、tsconfig.build.json，掌握构建发布。"))
    body.append(bullet("第五轮：读测试文件，掌握 mock、fake timers、jsdom 和组件测试边界。"))
    body.append(bullet("第六轮：按本文场景题练习，把项目实现和真实业务问题连起来。"))


def build_body() -> str:
    body: list[str] = []
    add_intro(body)
    add_stack_map(body)
    add_vue_ts(body)
    add_components(body)
    add_engineering(body)
    add_performance_browser(body)
    add_scenarios(body)
    add_ai_and_bottom(body)
    return "".join(body)


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:sz w:val="20"/><w:color w:val="1F2937"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="105" w:line="285" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="620" w:after="240"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="38"/><w:color w:val="163A6B"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="140"/><w:jc w:val="center"/></w:pPr><w:rPr><w:sz w:val="20"/><w:color w:val="52637A"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Meta"><w:name w:val="Meta"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="160"/></w:pPr><w:rPr><w:sz w:val="17"/><w:color w:val="667085"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="320" w:after="140"/><w:keepNext/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="27"/><w:color w:val="174A7C"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="230" w:after="105"/><w:keepNext/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="23"/><w:color w:val="245B84"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="180" w:after="70"/><w:keepNext/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:b/><w:sz w:val="20"/><w:color w:val="2F6F8F"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="180" w:after="180"/><w:ind w:left="360" w:right="240"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="5D8FD6"/></w:pBdr></w:pPr><w:rPr><w:i/><w:color w:val="3F4F63"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="StrongPara"><w:name w:val="StrongPara"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:color w:val="243B53"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="70"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="TableHeader"><w:name w:val="Table Header"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="15" w:line="220" w:lineRule="auto"/></w:pPr><w:rPr><w:b/><w:sz w:val="16"/><w:color w:val="163A6B"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="25" w:line="220" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="16"/><w:color w:val="1F2937"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="CalloutTitle"><w:name w:val="Callout Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="50"/></w:pPr><w:rPr><w:b/><w:sz w:val="19"/><w:color w:val="174A7C"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="CalloutText"><w:name w:val="Callout Text"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="35" w:line="260" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="18"/><w:color w:val="344054"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="35" w:after="35"/><w:ind w:left="260"/><w:shd w:fill="F4F7FB"/></w:pPr><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Microsoft YaHei"/><w:sz w:val="16"/><w:color w:val="1F4E79"/></w:rPr></w:style>
</w:styles>"""


def document_xml() -> str:
    sect = (
        '<w:sectPr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>'
        '</w:sectPr>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>{build_body()}{sect}</w:body>
</w:document>"""


def write_docx() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
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
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>"""
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>TinyElement 技术栈与项目深挖面试闭环</dc:title>
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
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="720"/>
</w:settings>"""
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
    print(str(OUT))
