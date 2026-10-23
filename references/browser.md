# Cola 浏览器适配

仅在调用参数不清、能力报错或电信需要移动环境时读本文件。入口和 GUIDE 已有业务流程，不再重复。

## 使用已启用的接口

遵循用户/宿主已有浏览器约定。若已指定 Ego，先读其已安装技能，复用本任务 TaskSpace、实际 spaceId 和页面标签；失败不自动切到 Cola 内置浏览器，不启用 legacy chrome_devtools。

Cola 已启用内置 `browser` 且无覆盖约定：

- 使用稳定的 `profile="cola"`；新业务只创建自己的页，已有任务用原 `targetId`，每次显式带 profile/targetId。不默认使用 `user` profile 或接管用户标签。关闭自己的页即可，不停止整个 profile，登录会话有效时可继续复用。
- `open` 可自动启动 profile，不先做 status/start/profiles/tabs 探测。只有调用失败或原 targetId 丢失时才检查对应状态；tabs 列表不能证明页面属于本任务。
- 原页面丢失且已有提交尝试时，新建页只能去官方入口查原订单，不再下单。登录和验证在原页交接，等本人确认；无法展示该页供本人操作时报告交接限制，不调用 focus 抢占窗口。
- 需要用户继续查看时保留订单/成功页，结束时只清理自己的无关页。Ego 按其技能结束/交接 TaskSpace。

以下 JSON 是传给 `browser` 的参数示例；其中 targetId 和 ref 必须替换为本次动作/快照真实返回值。

打开业务入口（URL 换成 GUIDE 中本次运营商入口）：

```json
{"action":"open","profile":"cola","targetUrl":"https://jf.10086.cn"}
```

一次快照读取业务字段和可操作 refs；`limit` 太小可能截断规则，缺什么再定向补读：

```json
{"action":"snapshot","profile":"cola","targetId":"本次返回的targetId","snapshotFormat":"ai","limit":100}
```

使用本次快照 ref 进行普通导航；DOM 或页面身份变化后重新取 refs。不要猜 selector，不批量连点：

```json
{"action":"act","profile":"cola","targetId":"本次返回的targetId","kind":"click","ref":"e1"}
```

已知需要等待的业务信号时，可用 `act/wait`，例如 `text="可用积分"`、`timeoutMs=8000`；这个文字出现不证明余额/面额已加载，仍要核对字段。不用固定 timeMs 或 networkidle 代替业务就绪。`act/evaluate` 需 fn 是函数源码字符串，详情见 [页面摘要](observe.md)。

`batch` 的数组在 `request.actions` 中，每项仍是 act 动作，不能塞 open/navigate/snapshot。仅当后续动作不需中间决策时合并；等待+只读摘要可合并，下单、扣分、短信请求逐步执行。整个批次包含开销应控制在工具约 20 秒的请求超时内。

## 能力失败

- `evaluate` 或函数条件等待被禁：不改配置，业务页退一次快照；验证页若快照不能排除输入值，就由本人确认非敏感状态，不采集整页输入。
- 页面字段不足：只补缺项；截图用于布局/图文规则，不凭模糊数字判断扣分或现金。
- 无浏览器工具或无法后台执行：明确缺少什么，提供官方入口和人工步骤，不安装工具、不切前台浏览器。本人完成后只读核对结果。
- 不复制浏览器配置、不导出 Cookie，不请求网页隐藏接口；已明确的工具错误不原样反复重试。

## 电信移动环境

2026-10-23 核对本地 Cola 副本 `cdeef1ff7`：内置工具支持 resize、evaluate、wait 和 batch，但未暴露 UA/设备模拟；该结论是适配基线，不代表其他版本。以目标会话实际工具定义和已配置能力为准，不重复扫描源码或尝试不存在的 action。

`resize` 不能设置请求 UA，`evaluate` 修改 navigator 也不能代替真实请求 UA。目标若只有上述内置接口，本技能无法自行补出移动环境：停在下单前，说明需 Cola 提供页面级 UA+移动视口能力，或由本人在手机官方页面办理。不私连控制端口、不改全局 UA。

若目标已提供设备模拟接口，使用其真实参数，在首次导航前设置手机 UA 和 390×844 移动视口。新弹页也需确认配置是否继承，不把旧页的设置当成全局生效。

已指定且可用的 Ego 支持页面级 CDP 时，在已归属本任务的 page 上执行：

```js
await page.cdp("Emulation.setUserAgentOverride", {
  userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
  acceptLanguage: "zh-CN,zh;q=0.9", platform: "iPhone",
});
await page.cdp("Emulation.setDeviceMetricsOverride", {
  width: 390, height: 844, deviceScaleFactor: 3, mobile: true,
});
```

这不是 Cola `browser` 的调用参数；不要把 page.cdp 填入 browser/evaluate。设备就绪后再走电信 GUIDE，页面回跳则查既有订单。
