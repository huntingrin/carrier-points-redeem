# 上游项目与许可证

本仓库把以下三个公开 Skill 作为子技能收录。整合层负责提问、校验和路由，不改变子技能的业务逻辑。

## 本地修改说明

为减少一次兑换的固定开销，对子技能做了下列最小修改。改动分两类：降低固定开销的交互调整，以及两处不改变范围的表述澄清（现金 0 的判定、对账是否再登录）。**业务范围没有扩大**：现金仍必须 0、只兑本机、状态不明不重复提交、验证码不进聊天。

| 文件 | 修改 | 原因 |
|---|---|---|
| `skills/cmcc-points-redeem/GUIDE.md` | 标注"本文件即完整流程"；已指定金额时直接输入，不展示面额表 | 避免 agent 额外查找参考文件 |
| `skills/cucc-points-redeem/GUIDE.md` | 浏览器流程改为"判读不清或排障时再读"；本地提交保护标注为默认不用；计划记录改为"一条简记录" | 正常路径少读 41 行、少一次调用 |
| `skills/ct-points-redeem/GUIDE.md` | 已指定面额跳过表格；授权改为"告知面额/积分/现金"而非二次确认，并给出四种必须停下的条件；补非 Ego 宿主的设备模拟写法与回跳兜底；对账改用同会话页面，`jf.189.cn` 的额外登录改为可选；本地提交保护标注为默认不用 | 少一轮人机交互，消掉"必须先知道积分才能授权"的死循环，并避免桌面 UA 重复下单 |
| `skills/ct-points-redeem/references/browser-flow.md` | 现金 0 的判定拆成"无现金行"与"有现金行但空白" | 原写法会把加载未完成判成现金 0 |

三份 `scripts/transaction_state.py` 与全部子技能测试**未修改**。上游更新时，按上表重放这几处文本改动即可同步。

## cmcc-points-redeem（中国移动）

- 仓库：https://github.com/huntingrin/cmcc-points-redeem
- 收录提交：`ae0e29b2d8801611565d2c9df2a7218eb9aa50d1`
- 许可证：MIT，见 `skills/cmcc-points-redeem/LICENSE`
- 保留内容：上游 `SKILL.md`（收录为 `GUIDE.md`）、`README.md`、`LICENSE`

## cucc-points-redeem（中国联通）

- 仓库：https://github.com/huntingrin/cucc-points-redeem
- 收录提交：`cc30fd46be01b99e015eae050efb77df0df216e7`
- 许可证：上游仓库未提供 LICENSE 文件，未声明许可证
- 保留内容：上游 `SKILL.md`（收录为 `GUIDE.md`）、`README.md`、`agents/`、`references/`、`scripts/`、`tests/`

## ct-points-redeem（中国电信）

- 仓库：https://github.com/huntingrin/ct-points-redeem
- 收录提交：`479b82e65936ba384cce9475067680a435da9c91`
- 许可证：上游仓库未提供 LICENSE 文件，未声明许可证
- 保留内容：上游 `SKILL.md`（收录为 `GUIDE.md`）、`README.md`、`agents/`、`references/`、`scripts/`、`tests/`

## 说明

- 未声明许可证的仓库，默认保留原作者全部权利。本仓库仅用于本地整合与个人使用；对外再分发、商用或打包发布前，请先向原作者确认授权。
- 三个子技能均为第三方社区项目，不是中国移动、中国联通或中国电信的官方产品。
- 子技能中的积分规则、商品、面额、资格和到账时间以各运营商官方页面及客服答复为准。
