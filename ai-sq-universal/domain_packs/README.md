# 领域包适配接口 / Domain Pack Adapter Interface

> 适用对象：为本 Skill 新增或修改 `domain_packs/*.yaml` 的作者。
> 范本（exemplar）：[science.yaml](science.yaml)。所有领域包必须与它**结构同构**——
> 相同的顶层键、相同的键序、相同的注释分节风格，只替换领域内容，不复制其科学术语。

## 1. 领域包是什么

本 Skill 的内核（kernel）是领域无关的：它只提供一套追问与取证的方法，不预设任何学科。
领域包（domain pack）是**方法到某个领域的适配器**（adapter）：把该领域的词汇、层级、
来源与风险边界映射到内核的通用机制上。没有领域包，内核仍然能工作，但会答得含糊；
有了领域包，同一个九层追问链才能问出"内行的问题"。

一句话区分：**内核管"怎么问"，领域包管"用什么词、问谁、信到什么程度、哪些话不能说"。**

| 职责 | 内核（kernel）负责 | 领域包（pack）负责 |
|---|---|---|
| 九层追问链（9-layer question chain） | 分层结构、递归下沉与收敛条件 | 每层在该领域用什么术语表达 |
| 证据链（evidence chain） | 证据节点、引用纪律、结论依赖关系 | 哪些来源算证据、按什么优先级取 |
| 缺口递归（gap-driven recursion） | 识别缺口、决定是否继续追 | 该领域"典型缺口"长什么样 |
| 范围与反例（scope & counterexample） | 通用反例检查框架与执行时机 | 领域必查的反例清单 |
| 层级校验（hierarchy validation） | 校验算法与"类别/实例"纪律 | 实体层级（粗 -> 细）的定义 |
| 停止控制（stop control） | 停止判据与质量门禁 | 领域"该停了"的信号 |
| 报告结构（report） | 报告骨架与证据等级标注 | 答案形态（表格/因果链/矩阵） |

## 2. 六个必需适配字段

领域包必须且只需在 YAML 中提供以下六个适配字段（其余键为展示与检索辅助）：

| # | 字段（YAML 键） | 作用（purpose） | 防止的失败（failure it prevents） |
|---|---|---|---|
| 1 | `entity_levels` | 定义 8–16 个粗 -> 细的实体层级 | 把类别属性套到实例、把协议行为当实现、把史家解释当史料 |
| 2 | `structure_semantics` | 定义 segment / copy / variant / unit / level / stage 的领域含义 | "几段/多少/几个"未消歧就作答，数字与量纲全错 |
| 3 | `authoritative_sources` | 4–7 个权威来源 + `priority`（1 最高），按序检索 | 一上来查百科、把二手当一手、把营销材料当文档 |
| 4 | `evidence_grades` | A/B/C/D 的领域细化 + `rules`（升降级规则） | 孤证升 A、预印本当共识、单次 anecdote 当实测 |
| 5 | `counterexample_rule` | 本领域必须执行的反例与边界检查（6–8 条） | 漏掉史料沉默、版本漂移、基准环境差异等致命反例 |
| 6 | `high_risk` + `high_risk_note` | 高风险边界、输出切割与免责要求 | 越过风险边界输出可操作危害细节、无中立性约束 |

字段 1–5 与"报告结构"章的第 3、5、6 节一一对应；字段 6 不属于报告章节，而是全局闸门。

### 2.1 字段粒度约定

- `entity_levels` 至少覆盖"承载物（载体）/ 要素 / 证据"三类，否则层级校验无处落锚。
- `structure_semantics.segment` 回答"本领域说'几段'时数的是什么"，且必须与 `unit` 正交
  （段数 vs 每段多少），否则"几段"与"多少"会互相污染。
- `structure_semantics` 六项必须全部用本领域词，允许为空想定，但不得留 `TODO`。
- `authoritative_sources` 的 `priority` 只表达**检索顺序**，不表达绝对可信度；同 `priority` 可并列多源。
- `evidence_grades.rules` 每条都应可判定（例："孤证最高 C"），避免"视情况而定"这类空规则。
- `counterexample_rule` 建议 6–8 条，按"最常见错误 -> 最致命错误"排序，先被读到的先执行。
- `disambiguation` 只收真正会改变答案的歧义词，不要为凑条数而填。

一个最小可用的结构语义骨架（值必须替换为本领域词）：

```yaml
structure_semantics:
  segment: 本领域"段/部分"数的是什么
  copy: 同一对象的多份拷贝指什么
  variant: 变体 / 版本 / 异文 / 配置档指什么
  unit: 计量单位（数量与量纲）
  level: 粗 < 中 < 细 的层级链
  stage: 时间或流程阶段
```

## 3. 优先级规则（最重要的一条）

**领域包可以"细化"，永远不可以"覆盖"内核。**

1. **不可覆盖**：反例检查、层级校验、停止规则、质量门禁（quality gates）由内核定义。
   领域包只能在领域内**追加**必查项，不得删减、不得放宽、不得改变执行时机。
2. **不可降级证据地板**：通用 A/B/C/D 地板不得整体下调。包可以更严（例如"孤证最高 C"），
   不可以更松（例如"官方文档可直接记 A"）。
3. **冲突以内核为准**：包与内核冲突时，按内核执行，并回到包内修订——不允许在包层面开例外。
4. **关系白名单封闭**：`relations` 只能取 exemplar 列表的子集，不得自造关系类型。
5. **风险边界单向**：包可以提高风险等级，不可以降低；高风险包输出的切割规则对所有下游生效。

## 4. 已发布的领域包（7 个）

| domain | display_name | `high_risk` | `structure_semantics.segment` 语义 |
|---|---|---|---|
| [science](science.yaml) | 科学 / Science | false | 结构域 / 外显子 / 操纵子 / 基因簇 / 通路步骤 / 实验分组 |
| [history](history.yaml) | 历史学 / History | false | 阶段 / 分期 / 史料层级 / 记载段落 |
| [technology](technology.yaml) | 技术 / Technology | false | 模块 / 层 / 接口 / 流水线阶段 |
| [law](law.yaml) | 法律 / Law | true | 条 / 款 / 项 / 目 |
| [finance](finance.yaml) | 金融 / Finance | true | 条款 / 分层（tranche）/ 档位 / 份额类别 |
| [policy](policy.yaml) | 政策 / Policy | true | 条款 / 阶段 / 试点批次 |
| [business](business.yaml) | 商业 / Business | false | 业务线 / SKU / 区域 / 合同条款 |

`high_risk: true` 的包在报告层强制加免责声明与"不提供可操作危害细节"切割；
`high_risk: false` 的包也必须写明**升级条件**（见各包 `high_risk_note`）。

## 5. 子包（sub_pack），而不是新 Skill

一个细分领域若只是"同一套方法、换一批术语"，不应拆成独立 Skill，而应降级为父包的子包。
范本：[science.yaml](science.yaml) 的 `sub_packs.bacteriology` 就是"细菌致病性"这一领域的
标准做法——它只覆盖 `domain` / `display_name` / `high_risk` / `entity_levels` / `relations` /
`structure_semantics` / `authoritative_sources` / `evidence_grades` / `counterexample_rule` /
`disambiguation` / `answer_patterns` / `stop_hints` / `failure_modes` / `frontier_sources`，
不引入任何新机制，也不改变内核逻辑。判断标准：

- 若新领域需要**新的推理机制**（如数值优化、形式化证明）-> 考虑独立 Skill；
- 若只是术语、层级、来源、证据分级不同 -> 写成一个 sub_pack。

## 6. 新增领域包 checklist（复制即用）

1. `cp domain_packs/science.yaml domain_packs/<new>.yaml`，保留全部分节注释与键序。
2. 填 `domain`（如 `medicine`）、`display_name`（中文 / English）、`version: 1.0.0`、`extends: null`。
3. 判定 `high_risk`：涉及人身安全、法律后果、财产损失、生物/信息安全、政治敏感即 `true`；
   无论真假，都要写清 `high_risk_note` 的升级条件与输出切割。
4. 写 `entity_levels`：8–16 项，粗 -> 细，必须能区分该领域的"载体 vs 要素"。
5. 写 `structure_semantics` 六项，全部用领域词，禁止照抄其它包（尤其 `segment`）。
6. `relations` 从范本白名单取子集（不得自造）；`authoritative_sources` 4–7 项，
   `priority` 1 -> 5 递增，百科类永远放最后。
7. 细化 `evidence_grades`：A/B/C/D + `rules`，只收紧不放松；`counterexample_rule` 写 6–8 条
   领域必查反例；`disambiguation` 写 3–5 条真实歧义词。
8. 写 `answer_patterns`（3 类：清单/机制/范围）、`stop_hints`（4–5 条）、`frontier_sources`（4–5 条）。
9. 跑下面的校验命令，确认输出 `OK` 且 A/B/C/D 四个字母齐全；再人工自检无 tab、无 `sub_packs`、
   `relations` 未越界、无 ASCII 冒号未加引号的裸标量。
10. 在本文第 4 节表格补一行（domain / high_risk / `segment` 语义），并在改动说明里列出
    "细化了哪些项、如何保证没有覆盖内核规则"。

```bash
python -c "import yaml,sys;d=yaml.safe_load(open(sys.argv[1],encoding='utf-8'));req=['domain','display_name','version','extends','high_risk','high_risk_note','entity_levels','relations','structure_semantics','authoritative_sources','evidence_grades','counterexample_rule','disambiguation','answer_patterns','stop_hints','frontier_sources'];miss=[k for k in req if k not in d];print(sys.argv[1],'OK' if not miss else 'MISSING '+str(miss),'| grades',sorted(d.get('evidence_grades',{}).keys()))" "domain_packs/<new>.yaml"
```

预期输出形如 `<new>.yaml OK | grades ['A', 'B', 'C', 'D', 'rules']`。
`rules` 是 `evidence_grades` 下必带的细分规则块；验收只看 `A`/`B`/`C`/`D` 四个字母是否齐全。

## 7. 常见写包错误

- 把领域包写成"内容百科"：包只放适配规则，不放大段领域知识。
- `segment` 直接抄 science 的"结构域/外显子"，导致其它领域答非所问。
- 为方便检索把百科塞进 priority 1–2，破坏来源优先级。
- 在 `rules` 里悄悄放宽证据地板（如"预印本可升 A"），这是最严重的违规。
- 忘记 `high_risk_note`：高风险领域没有输出切割，等于没有边界。
