# 插件层说明（plugin/）

这个目录**不是**一个 npm 包。它做两件事：

1. **`plugin.json`** —— 本 Skill 包的机器可读清单：名称、版本、贡献的 skill、依赖的 DSH 插件、安装方式、风险策略。
2. **`cordis.patch.yml`** —— 一个真实的 **Cordis 组合补丁**：把本包所在目录注册为 DSH 的额外“技能根”，让 `ai-sq-universal` 出现在技能目录里，而文件留在仓库原地。

安装器 `install.ps1`（Windows）与 `install.sh`（macOS/Linux）把这两件事串起来。

---

## 为什么有两种安装方式

DSH 的 skill 发现规则是：扫描若干“技能根”，每个根下面的一级子目录里若有 `SKILL.md`，就当成一个 skill（即 `<root>/<name>/SKILL.md`）。

| 方式 | 做法 | 适合谁 | 代价 |
|---|---|---|---|
| **copy**（默认） | 把 `ai-sq-universal/` 复制到 `~/.dsh/skills/ai-sq-universal` | 只想用，不想碰配置 | 升级时要重跑一次 |
| **plugin** | 不复制，用 Cordis 补丁把本包根目录注册成额外技能根 | 想把包放在仓库里、跟着 git 更新 | 需要把补丁并入 `~/.dsh/cordis.patch.yml` |

copy 模式**不需要任何配置**——`~/.dsh/skills` 本来就是默认用户技能根。插件模式解决的是“我想让技能留在项目里”这个需求。

---

## 路由一：copy（推荐先试这个）

```powershell
cd plugin
.\install.ps1                 # Windows
```

```bash
cd plugin && ./install.sh     # macOS / Linux
```

做的事：

1. 确认 `ai-sq-universal/SKILL.md` 存在；
2. 若 `~/.dsh/skills/ai-sq-universal` 已存在 → **改名为 `.bak-<时间戳>`**（不删除，可回滚）；
3. 复制整个 skill 目录；
4. 校验目标里的 `SKILL.md` 确实到位。

重启 DSH 或开新会话后，技能目录里应出现 `ai-sq-universal-root-inquiry`。

---

## 路由二：plugin（技能留在原地）

```powershell
cd plugin
.\install.ps1 -Mode plugin
```

```bash
cd plugin && ./install.sh plugin
```

生成 `cordis.patch.generated.yml`，其中 `__SKILL_ROOT__` 已替换为**本包根目录的绝对路径**（注意是 `ai-sq-universal` 的**父目录**，因为 `customSkillDirs` 指的是技能根，不是 skill 目录本身）。

然后手动把 `insert:` 段并入 `~/.dsh/cordis.patch.yml`，重启 DSH。

**安装器不会自动改你的配置。** 机器拼接 YAML 是安装脚本最常见的破坏方式——你的配置里可能已有 MCP、provider、自定义根，多一个缩进错误就整段失效。所以这里只生成文件、打印说明，合并这一步留给你。

补丁长这样（生成后路径已填好）：

```yaml
- insert:
    - id: ai-sq-root-inquiry-skills
      name: "@deepseek-ai/dsh-skill-filesystem"
      config:
        providerName: aisq-root-inquiry
        includeDefaultRoots: false
        customSkillDirs:
          - "D:\\DEVELOP\\AI-SQ-Universal-Root-Inquiry"
        watch: true
```

`includeDefaultRoots: false` + 独立 `providerName`：只新增一个“只读本目录”的 provider，**不改变**原有的 project/user 技能根，因此不会与默认发现冲突，也不会让别的技能消失或重复。

---

## 自检

```powershell
.\install.ps1 -Mode verify
```

检查项：

- `SKILL.md` 的 frontmatter（`name` 必须是 kebab-case，`description` 非空且足够长）
- 必备文件布局（5 个提示词、4 个 schema、模板、评测集、示例）
- 7 个领域包的结构（必填键、`entity_levels` 数量、`relations` 白名单、A/B/C/D 证据等级、`sub_packs` 完整性）
- 评测集：10 个案例、id 唯一、覆盖面

就是跑 `ai-sq-universal/scripts/validate.py`，所以也可以直接单独跑：

```bash
python ai-sq-universal/scripts/validate.py
```

---

## 依赖

| 依赖 | 用途 | 缺失时 |
|---|---|---|
| `@deepseek-ai/dsh-skill` | 技能注册表 | 技能不出现 |
| `@deepseek-ai/dsh-skill-filesystem` | 从磁盘发现技能（plugin 模式必需；copy 模式由默认根覆盖） | 同上 |
| Python ≥ 3.8 + PyYAML | `validate.py` / `quality_gate.py` | 技能仍可用，只是自检与门禁不可自动化 |

Skill 本体（SKILL.md + prompts + schemas + packs）是纯文本，**不依赖任何运行时**。

---

## 卸载

**copy 模式**：删掉 `<skills>/ai-sq-universal`（以及你保留的 `.bak-*`）。

```powershell
Remove-Item -Recurse -Force "$HOME\.dsh\skills\ai-sq-universal"
```

**plugin 模式**：从 `~/.dsh/cordis.patch.yml` 删掉 `ai-sq-root-inquiry-skills` 那一段，重启 DSH。

技能目录是纯文件，没有任何后台进程、开机项、注册表写入或网络监听——卸载就是删文件。

---

## 安全与边界

- 安装器只做**文件复制**与**补丁文本生成**；不联网、不执行下载内容、不修改 PATH 或注册表。
- 覆盖安装前一律先改名备份，不静默删除你的东西。
- `plugin.json` 只是清单，DSH 不会因为它在而自动装任何东西——安装必须由你显式跑安装器。
- 高风险领域（医学/法律/金融/安全/政策/心理）的输出必须带免责声明与人工复核建议；技能不提供可执行的危险操作细节。
