# 上游项目与许可证

本仓库把以下三个公开 Skill 作为子技能原样收录。整合层只负责提问、校验和路由，不改变子技能的业务逻辑。

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
