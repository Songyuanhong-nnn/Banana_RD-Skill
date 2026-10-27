# Factor Mapper｜因素空间展开器

**作用**：把一个"结果 Y"的影响因素**铺开成空间**，而不是顺着一条链往下走。九层追问链解决"挖多深"，这里解决"铺多全"。

**为什么必须有这一步**：给一个问题的回答打分，最容易骗过自己的方式是"机制讲得很漂亮"。但真实问题通常是多因素共同作用——只挖到一条链，另外八大类因素根本没被想到过。**记忆只会重复你已经想到的类别**，所以要按轴机械枚举。

**什么时候用**：复杂度 L2 及以上。L1（单链）不用建因素空间，强行建只会产出凑数的空表格。

**输入**：目标结果 / 待解释现象、领域包（`entity_levels` / `structure_semantics`）、已收集的证据与机制结论、复杂度档位。

**输出**：因素数组 + 轴覆盖表，JSON。

---

## 一、先按九轴枚举（不是按记忆枚举）

逐轴过，每轴问一次"这里有没有因素"。**空轴必须写"空 + 理由"**，不许留白——留白与"确认没有"是两件事。

| # | 轴 | 该问什么 | 领域内怎么落地（示例） |
|---|---|---|---|
| 1 | 时间 | 起源、阶段、时滞、累积暴露、演化 | 病程阶段、政策试点批次、协议版本 |
| 2 | 空间/层级 | 分子→细胞→个体→群体→制度→全球 | 菌株 vs 物种、个人 vs 行业、地方 vs 中央 |
| 3 | 主体 | 行为者、利益相关方、权力与激励 | 监管者、经营者、患者、渠道商 |
| 4 | 物质/资源 | 能量、资金、材料、算力、人力、供给约束 | 营养/铁离子、资本开支、产能 |
| 5 | 规则/制度 | 法律、规范、激励、准入、监管 | 条文、司法解释、会计准则、行业标准 |
| 6 | 信息/认知 | 知识、信息不对称、预期、偏差 | 检测覆盖率、市场预期、诊断延迟 |
| 7 | 技术/工具 | 能力、成本、可用性、成熟度 | 检测方法、T3SS、算法版本 |
| 8 | 环境/外部冲击 | 气候、市场、地缘、随机事件 | 温度/pH、集采政策、疫情 |
| 9 | 反馈/动态 | 正反馈、负反馈、锁定、相变、临界点 | 耐药选择压、份额-成本循环 |

**选轴不是走形式**：每轴至少产出一个候选因素，或产出一句"该轴为空，因为 ⟨机制上不可能/已确认无影响⟩"。后者本身就是结论。

---

## 二、每个因素必须写清六件事

```json
{
  "factor_id": "F1",
  "name": "Stx2 表达水平",
  "axis": "物质/资源",
  "entity_level": "protein_effector",
  "role": "necessary|sufficient|contributing|inhibiting|threshold|moderator|mediator|confounder",
  "direction": "+|-|±",
  "magnitude": "dominant|major|minor|unknown",
  "magnitude_basis": "为何是这个量级",
  "proxy": "可观测代理",
  "evidence_ids": ["E1", "E4"],
  "evidence_grade": "A",
  "how_to_test": "怎样验证它真的起作用",
  "strata_dependence": "在哪些分层上效应不同（L3 起必填）"
}
```

**逐项要求：**

1. **`role` 比"重要/不重要"有用得多**。必要条件被去掉会直接改变结论；促进因素只是加速；调节因素改变别人的强度——三种的处置方式完全不同。
2. **`magnitude` 必填，`unknown` 必须带原因**。原因只认三种：无量化研究、证据冲突、不可观测。写"影响比较复杂"不算原因。
3. **`magnitude_basis` 是给读者的诚实度检查**。写不出依据的量级就是猜的——那就老实标 `unknown`。
4. **`proxy` 决定这个因素能不能被验证**。没有代理的因素，结论只能停在"理论上有影响"。
5. **`how_to_test` 是给下一步追问的接口**。写不出验证方式的，通常说明这个因素还没想清楚。

---

## 三、量级判定规则（避免"都很重要"）

| 量级 | 操作化判据 | 报告里怎么写 |
|---|---|---|
| `dominant` | 单独解释大部分结果，或为必要条件（去掉则结果不发生） | "主因：⟨因素⟩（去掉则 Y 不发生）" |
| `major` | 显著改变幅度，但不决定有无 | "重要影响因素，量级约 ⟨…⟩" |
| `minor` | 影响可测但有限 | "次要因素，仅在 ⟨条件⟩ 下可观测" |
| `unknown` | 无量化/冲突/不可观测 + 原因 | "影响方向已知（+），量级未知（无量化研究）" |

**禁止产出**："上述因素都很重要，需综合考虑"。这句话的信息量为零，是本环节的典型失败产物。

---

## 四、轴覆盖表（输出的一部分）

```json
{
  "axis_coverage": [
    {"axis": "时间", "factors": ["F3"], "status": "covered"},
    {"axis": "主体", "factors": [], "status": "empty", "reason": "该结果由物理机制决定，无行为主体参与"},
    {"axis": "反馈/动态", "factors": [], "status": "unchecked", "reason": "L2 档不要求，但可能隐藏时滞"}
  ],
  "negative_space": [
    "按常识应有'检测覆盖率'因素，但未找到本研究语境下的证据 —— 这是当前最大漏洞"
  ]
}
```

- `status` 三态：`covered` / `empty`（确认无）/ `unchecked`（没查）。**`unchecked` 必须出现在报告 §14**，不许在成稿里消失。
- `negative_space` 是"应该存在但我没找到"的清单。它比已找到的因素更有价值——**已找到的写在正文，没找到的写在风险里**。

---

## 五、与九层链的衔接

| 九层链产出 | 因素空间怎么用 |
|---|---|
| 第 3 层机制链 | 链上每个节点 → 一个候选因素（`role` 多为 necessary/contributing） |
| 第 4 层要素清单 | 每个要素 → 一个候选因素（注意：要素存在 ≠ 起主导作用） |
| 第 7 层调控约束 | 调控者 → `role: moderator` 或 `threshold` |
| 第 8 层证据争议 | 冲突点 → 常是 `magnitude: unknown` 的原因 |

**不要把要素清单直接当因素清单。** "有 12 个毒力基因"与"12 个因素都重要"是两句话；后者必须逐个给量级，而多数会是 `minor` 或 `unknown`。

---

## 示例（L2：O157:H7 致病性的因素空间，节选）

```json
[
  {"factor_id":"F1","name":"Stx2 表达水平","axis":"物质/资源","entity_level":"protein_effector",
   "role":"necessary","direction":"+","magnitude":"dominant",
   "magnitude_basis":"HUS 病例中 stx2a 亚型显著富集；缺失突变丧失细胞毒性",
   "proxy":"Vero 细胞毒性滴度 / stx2 转录量","evidence_ids":["E1","E4"],"evidence_grade":"B",
   "how_to_test":"缺失突变 + 回补；Vero 细胞试验"},
  {"factor_id":"F2","name":"感染剂量","axis":"物质/资源","entity_level":"mechanism",
   "role":"threshold","direction":"+","magnitude":"major",
   "magnitude_basis":"暴发调查显示极低 ID50；剂量与罹患率正相关",
   "proxy":"暴露剂量回溯估算","evidence_ids":["E4"],"evidence_grade":"B",
   "how_to_test":"暴发剂量反应分析"},
  {"factor_id":"F3","name":"宿主免疫状态与年龄","axis":"主体","entity_level":"host_cell",
   "role":"moderator","direction":"±","magnitude":"major",
   "magnitude_basis":"儿童/老年 HUS 风险更高；亚组效应方向一致",
   "proxy":"年龄分层发病率","evidence_ids":["E4"],"evidence_grade":"B",
   "how_to_test":"分层队列分析","strata_dependence":"儿童 vs 成人 vs 免疫抑制"},
  {"factor_id":"F4","name":"抗生素使用","axis":"规则/制度","entity_level":"intervention",
   "role":"moderator","direction":"-","magnitude":"unknown",
   "magnitude_basis":"证据冲突：部分研究示 HUS 风险升高，部分示无关联",
   "proxy":"用药记录 + HUS 发生率","evidence_ids":["E5"],"evidence_grade":"B",
   "how_to_test":"倾向评分匹配队列","strata_dependence":"菌株/用药时机可能改变方向"}
]
```

注意 F4：`unknown` 不是偷懒，是**证据冲突的正确表达**。把它写成 "major" 或删掉都是失真。

---

## 反模式

| 反模式 | 后果 |
|---|---|
| 只从机制链取因素 | 漏掉主体、制度、信息、外部冲击四整类 |
| 因素清单无量级 | "都很重要"= 没回答 |
| `unknown` 不写原因 | 读者无法判断是没查还是查不到 |
| 把空轴留白 | 无法区分"确认无"与"没想到" |
| 把要素清单当因素表 | 12 个基因 ≠ 12 个主导因素 |
| L1 问题硬建因素空间 | 产出凑数表格，浪费预算 |
| `negative_space` 不写 | 最大的漏洞永远不出现 |
