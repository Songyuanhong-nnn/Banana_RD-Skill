# 安装与验证

三种安装路由，按你的情况选一个。全部为**纯文件操作**：不联网、不写注册表、不加开机项。

| 你的情况 | 用哪个 | 需要改配置吗 |
|---|---|---|
| 只想用 | **copy**（默认） | 不需要 |
| 想把包放在仓库里、跟着 git 更新 | **plugin** | 需要并入一段 Cordis 补丁 |
| 只想检查包是否完整 | **verify** | 不需要 |

---

## 0. 前置条件

| 项 | 要求 | 检查 |
|---|---|---|
| DSH 版本 | ≥ 0.2.0 | `dsh --version` |
| 必需插件 | `@deepseek-ai/dsh-skill`、`@deepseek-ai/dsh-skill-filesystem` | 默认已装 |
| Python（可选） | ≥ 3.8 + PyYAML，仅 `validate.py` / `quality_gate.py` 需要 | `python -c "import yaml;print(yaml.__version__)"` |

**Skill 本体是纯文本**，没有 Python 也能用，只是自检与门禁不能自动化。

---

## 1. copy 模式（推荐）

### Windows

```powershell
cd AI-SQ-Universal-Root-Inquiry\plugin
.\install.ps1
```

### macOS / Linux

```bash
cd AI-SQ-Universal-Root-Inquiry/plugin
chmod +x install.sh
./install.sh
```

### 它做了什么

1. 确认 `../ai-sq-universal/SKILL.md` 存在
2. 若 `~/.dsh/skills/ai-sq-universal` 已存在 → 改名为 `.bak-<时间戳>`（**不删除**）
3. 复制整个 skill 目录
4. 校验目标中的 `SKILL.md` 到位

结果：

```text
~/.dsh/skills/ai-sq-universal/
├── SKILL.md
├── prompts/  schemas/  domain_packs/  templates/  evals/  examples/  scripts/
```

`~/.dsh/skills` 是 DSH 的默认用户技能根，**不需要任何配置**。

### 手动等价操作（不想跑脚本时）

```powershell
# Windows
Copy-Item -Recurse -Force .\ai-sq-universal "$HOME\.dsh\skills\ai-sq-universal"
```

```bash
# macOS / Linux
cp -R ./ai-sq-universal ~/.dsh/skills/
```

---

## 2. plugin 模式（技能留在原地）

```powershell
cd plugin
.\install.ps1 -Mode plugin
```

```bash
cd plugin && ./install.sh plugin
```

生成 `plugin/cordis.patch.generated.yml`，`__SKILL_ROOT__` 已替换为**本包根目录的绝对路径**。

然后：

1. 打开 `~/.dsh/cordis.patch.yml`
2. 把生成文件里的 `insert:` 段并入（注意与已有条目同级缩进）
3. 重启 DSH

**安装器不会自动改你的配置。** 机器拼接 YAML 是安装脚本最经典的破坏方式——多一个缩进错误整段失效。合并这一步留给人。

生成的补丁：

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

**路径要点**：`customSkillDirs` 指向的是**技能根**（含 `<name>/SKILL.md` 的那一层），也就是 `ai-sq-universal` 的**父目录**，不是 `ai-sq-universal` 本身。

`includeDefaultRoots: false` + 独立 `providerName` 的效果：只新增一个只读本目录的 provider，原有的 project/user 技能根不受影响，不会让别的技能消失或重复出现。

---

## 3. verify 模式（自检）

```powershell
.\install.ps1 -Mode verify
```

```bash
./install.sh verify
```

即运行 `ai-sq-universal/scripts/validate.py`，检查：

- `SKILL.md` frontmatter：`name` 为 kebab-case、`description` 非空且足够长、有 `version` / `triggers` / `not_for`
- 文件布局：5 个提示词、4 个 schema、模板、评测集、示例
- 7 个领域包：必填键齐全、`entity_levels` 6–20 项、`relations` 在白名单内、`structure_semantics` 三项齐全、`authoritative_sources` 带 priority、`evidence_grades` 含 A/B/C/D、`high_risk` 为布尔、`sub_packs` 结构完整
- 评测集：10 案、id 唯一、字段齐全、领域多样性

也可单独跑：

```bash
python ai-sq-universal/scripts/validate.py
python ai-sq-universal/scripts/validate.py --packs     # 只查领域包
python ai-sq-universal/scripts/validate.py --json      # 机器可读
```

退出码 `0` = 全过，`1` = 有失败项。

---

## 4. 确认生效

1. 重启 DSH，或开一个新会话
2. 看技能目录里是否有 `ai-sq-universal-root-inquiry`
3. 说一句带触发词的话，例如：「求根问底调研一下 ⟨对象⟩，要证据链和反例」

---

## 5. 排错

| 现象 | 原因 | 修法 |
|---|---|---|
| 技能目录里没有它 | 目录层级不对 | 必须是 `<skills>/ai-sq-universal/SKILL.md`，不是 `<skills>/AI-SQ-Universal-Root-Inquiry/ai-sq-universal/SKILL.md` |
| 同上 | `name` 不是 kebab-case | `name` 只能 `[a-z0-9-]`，且不能以 `-` 开头/结尾 |
| 同上 | frontmatter 解析失败 | 文件必须严格以 `---` 开头，第二段 `---` 收尾；YAML 不能用 Tab |
| 同上 | 没重启 | 新开一个会话 |
| plugin 模式不生效 | 路径填成了 skill 目录本身 | 改填**父目录** |
| plugin 模式不生效 | 补丁缩进错了 | 与 `cordis.patch.yml` 里其它 `- insert:` 条目同级 |
| `validate.py` 报 `ModuleNotFoundError: yaml` | 没装 PyYAML | `pip install pyyaml` |
| 技能出现两个 | copy 模式与 plugin 模式同时启用 | 二选一：删掉 `~/.dsh/skills/ai-sq-universal`，或去掉 Cordis 补丁 |
| 中文乱码 | 终端编码 | `chcp 65001`（Windows），或 `$env:PYTHONIOENCODING='utf-8'` |

---

## 6. 卸载

**copy 模式**

```powershell
Remove-Item -Recurse -Force "$HOME\.dsh\skills\ai-sq-universal"
```

```bash
rm -rf ~/.dsh/skills/ai-sq-universal
```

**plugin 模式**：从 `~/.dsh/cordis.patch.yml` 删掉 `ai-sq-root-inquiry-skills` 那段，重启 DSH。

**备份目录**（`.bak-<时间戳>`）确认新版没问题后自行删除。

---

## 7. 升级

1. 用新包覆盖（copy 模式直接重跑安装器：旧目录会被改名备份，不丢东西）
2. 跑 `verify`
3. 看 `CHANGELOG.md` 有没有破坏性变更（如 schema 字段改名、领域包接口变更）

领域包是数据文件，**可以单独替换**而不动内核：改完跑 `validate.py --packs` 即可。
