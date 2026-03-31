import type { App, Plugin } from 'vue'
import './styles/index.css'

import Button from './components/Button'
import Container from './components/Container'
import Header from './components/Container/Header.vue'
import Footer from './components/Container/Footer.vue'
import Main from './components/Container/Main.vue'
import Aside from './components/Container/Aside.vue'
import ButtonGroup from './components/ButtonGroup/ButtonGroup.vue'
import Icon from './components/Icon/Icon.vue'
import Link from './components/Link/Link.vue'
import Alert from './components/Alert/Alert.vue'
import Collapse from './components/Collapse/Collapse.vue'
import CollapseItem from './components/Collapse/CollapseItem.vue'
import Tooltip from './components/Tooltip'
import Dropdown from './components/Dropdown'
import Input from './components/Input/Input.vue'
import Rate from './components/Rate/Rate.vue'
import DatePicker from './components/DatePicker/DatePicker.vue'
import Switch from './components/Switch/Switch.vue'
import Select from './components/Select/Select.vue'
import Form, { FormItem } from './components/Form'
import Dialog from './components/Dialog'
import Message from './components/Message'
import MessageBox from './components/MessageBox/MessageBox'

type SFCWithInstall<T> = T & Plugin

const withInstall = <T extends { name: string }>(component: T) => {
  const target = component as SFCWithInstall<T>
  if (!target.install) {
    target.install = (app: App) => {
      app.component(target.name, target)
    }
  }
  return target
}

const ElHeader = withInstall(Header)
const ElFooter = withInstall(Footer)
const ElMain = withInstall(Main)
const ElAside = withInstall(Aside)
const ElButtonGroup = withInstall(ButtonGroup)
const ElIcon = withInstall(Icon)
const ElLink = withInstall(Link)
const ElAlert = withInstall(Alert)
const ElCollapse = withInstall(Collapse)
const ElCollapseItem = withInstall(CollapseItem)
const ElInput = withInstall(Input)
const ElRate = withInstall(Rate)
const ElDatePicker = withInstall(DatePicker)
const ElSwitch = withInstall(Switch)
const ElSelect = withInstall(Select)

const components = [
  Button,
  Container,
  ElHeader,
  ElFooter,
  ElMain,
  ElAside,
  ElButtonGroup,
  ElIcon,
  ElLink,
  ElAlert,
  ElCollapse,
  ElCollapseItem,
  Tooltip,
  Dropdown,
  ElInput,
  ElRate,
  ElDatePicker,
  ElSwitch,
  ElSelect,
  Form,
  FormItem,
  Dialog
] as Plugin[]

const installer: Plugin = {
  install(app: App) {
    components.forEach((component) => {
      app.use(component)
    })
    app.use(Message)
    app.config.globalProperties.$messageBox = MessageBox
  }
}

export default installer

export {
  Button,
  Container,
  ElHeader as Header,
  ElFooter as Footer,
  ElMain as Main,
  ElAside as Aside,
  ElButtonGroup as ButtonGroup,
  ElIcon as Icon,
  ElLink as Link,
  ElAlert as Alert,
  ElCollapse as Collapse,
  ElCollapseItem as CollapseItem,
  Tooltip,
  Dropdown,
  ElInput as Input,
  ElRate as Rate,
  ElDatePicker as DatePicker,
  ElSwitch as Switch,
  ElSelect as Select,
  Form,
  FormItem,
  Dialog,
  Message,
  MessageBox
}

export * from './components/Button/types'
export * from './components/Container/types'
export * from './components/Link/types'
export * from './components/Alert/types'
export * from './components/Collapse/types'
export * from './components/Tooltip/types'
export * from './components/Dropdown/types'
export * from './components/Input/types'
export * from './components/Rate/types'
export * from './components/Switch/types'
export * from './components/Select/types'
export * from './components/Form/types'
export * from './components/Dialog/types'
export * from './components/Message/types'
export * from './components/MessageBox/types'
