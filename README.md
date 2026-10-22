# 三网积分兑换统一入口

把 huntingrin 的三个运营商积分兑换 Skill 收进一个入口：

| 运营商 | 子技能 | 能力 |
|---|---|---|
| 中国移动 | `cmcc-points-redeem` | 现有 AI 豆兑本机话费，现金补款 0 元 |
| 中国联通 | `cucc-points-redeem` | 积分兑流量包、语音包、影音组合；话费走 `10010` 短信文字方法 |
| 中国电信 | `ct-points-redeem` | 积分兑本机话费直充，现金补款 0 元 |

用户只需要在**一句话**里给出运营商和手机号，剩下的路由、登录交接、选品、短信验证和结果核对按对应子技能执行。

## 目录结构

```text
.
├── SKILL.md                    # 唯一入口：提问、校验、路由
├── README.md
├── THIRD_PARTY.md              # 上游仓库、提交与许可证说明
├── LICENSE                     # 仅覆盖本仓库新增的整合层
├── agents/openai.yaml          # 宿主展示信息
├── install.sh                  # 静默安装
├── uninstall.sh                # 卸载
├── skills/
│   ├── cmcc-points-redeem/     # 移动
│   ├── cucc-points-redeem/     # 联通
│   └── ct-points-redeem/       # 电信
└── tests/
    └── test_install.sh         # 安装/重复安装/卸载的离线测试
```

三个子技能保留上游的说明书、`references/`、`scripts/` 和测试，仅去掉了与运行无关的调研与实测记录目录。子技能说明书统一命名为 `GUIDE.md`，避免宿主把嵌套目录也识别成独立技能；入口按路由结果读取对应的 `GUIDE.md`。

## 静默安装

安装阶段无交互、无配置、无 API Key。一条命令把总技能和三个子技能一起放好：

```sh
./install.sh
```

默认行为：

- 检测到 `~/.codex`、`~/.cola` 或 `~/.claude` 时，安装到对应的 `skills/` 目录；
- 一个都没检测到时，安装到 `~/.codex/skills/carrier-points-redeem`；
- 已存在同名目录时整体替换，可重复执行。

指定目标：

```sh
./install.sh --target codex     # ~/.codex/skills
./install.sh --target cola      # ~/.cola/skills
./install.sh --target claude    # ~/.claude/skills
./install.sh --target ~/my-skills
```

如果宿主的 `skills/` 目录里已经装了独立的 `cmcc-points-redeem`、`cucc-points-redeem`、`ct-points-redeem`，默认会保留它们，入口技能仍可正常工作。想让入口成为唯一技能，可加归档开关：

```sh
./install.sh --archive-standalone
```

它会把旧的三个独立目录移到同级的 `.carrier-points-redeem-archive-<时间戳>/`，不删除。需要回滚时，先 `./uninstall.sh` 卸载入口，再把归档目录里的子技能移回 `skills/` 即可。

安装后的结构：

```text
~/.codex/skills/carrier-points-redeem/
├── SKILL.md
├── skills/
│   ├── cmcc-points-redeem/
│   ├── cucc-points-redeem/
│   └── ct-points-redeem/
└── ...
```

宿主只看到 `carrier-points-redeem` 一个技能；子技能由入口按需读取，不会单独出现在技能列表里。

卸载：

```sh
./uninstall.sh
./uninstall.sh --target ~/my-skills
```

## 使用

安装后直接说：

> 帮我兑换积分，移动 13800138000

或：

> 联通 13900139000，看看积分能换什么
>
> 联通 13900139000，话费怎么换

入口只会问一次：

> 请告诉我你的运营商和手机号，例如：移动 13800138000

用户同时给出两项后，入口校验格式，直接路由，不再追问“你是哪个运营商”。

路由规则：

- 移动 → `skills/cmcc-points-redeem/GUIDE.md`
- 联通 → `skills/cucc-points-redeem/GUIDE.md`
- 电信 → `skills/ct-points-redeem/GUIDE.md`

## 设计约束

- **不猜运营商**：运营商由用户明说，不根据号段推断，避免携号转网误路由。
- **只支持三网**：广电、虚拟运营商、170/171 等号段会明确说明不支持，不硬路由。
- **本机业务**：三个子技能都只办理当前登录号码的业务；登录号码与用户提供号码不一致时停止。
- **验证码不进聊天**：登录、图形码、短信验证都由用户本人在官方页面完成。
- **不重复提交**：扣积分不等于到账，提交订单不等于兑换成功；状态不明时先只读核对。
- **联通话费是文字方法**：走 `10010` 短信，不是商城商品；不登录商城、不发短信、不生成二维码，具体规则以 `10010` 回复为准。
- **手机号脱敏**：对外展示、日志和任务记录使用 `138****8000`，完整号码不写入安装目录。

## 测试

```sh
bash tests/test_install.sh
```

测试在临时目录中执行安装、重复安装和卸载，不访问网络。

## 来源与许可证

三个子技能来自 huntingrin 的公开仓库，提交号和许可证状态见 [THIRD_PARTY.md](THIRD_PARTY.md)。

本仓库新增的整合层（入口 `SKILL.md`、安装脚本、说明文档）使用 MIT License；该许可不改变三个子技能各自的版权与许可状态。
