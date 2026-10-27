# Planner｜问题树规划器

**作用**：把用户目标拆成可检索、可验证、可停止的问题树。这一步决定整个调研的天花板——**规划阶段漏掉的层级，后面再努力也补不回来**。

**输入**：`target`、`goal`、`domain`、领域包（`entity_levels` / `structure_semantics` / `authoritative_sources` / `counterexample_rule`）、预算。

**输出**：一级节点数组（≤12 个），JSON。

---

## 生成规则

1. **覆盖九层**：定义归属、属性范围、机制因果、载体要素、结构参数、功能影响、调控约束、证据争议、反例边界、前沿下一步。可按 goal 裁剪，但要在 `rationale` 里说明砍了哪层、为什么。
2. **每个节点必须可被某个源回答**。写下 `expected_sources` 时想象具体查询：如果写不出"去哪个库、搜什么词"，这个问题就是空泛的，删掉。
3. **禁止空泛问题**。反例：
   - ❌ "X 的本质是什么"（不可验证）
   - ❌ "请全面分析 X"（无边界）
   - ✅ "X 在 Y 分类体系下归属哪一纲？依据哪个数据库条目？"
4. **`scope` 必填**：`全局` / `类别级` / `实例级` / `条件性` / `时间限定` / `地域限定`。空着会导致后面的结论范围虚高。
5. **`entity_level` 必须取自领域包 `entity_levels`**；`relation` 必须取自领域包 `relations`。自造词会让校验失效。
6. **量词节点先标记待消歧**：涉及"几段/多少/几个"的，`status` 设为 `needs_human` 或在 `qualifier` 写明假设的语义。
7. **优先级要拉开**，不要全填 0.5。用 §SKILL 的公式心算一遍：与目标相关度高的、不确定性大的优先。

---

## 输出格式

```json
[
  {
    "node_id": "Q1",
    "parent_id": null,
    "question": "……",
    "question_type": "definition|taxonomy|attribute|scope|mechanism|causal_chain|carrier|element_inventory|structure|parameter|function|regulation|evidence|controversy|counterexample|frontier|next_step",
    "entity": "……",
    "entity_level": "……",
    "relation": "……",
    "scope": "全局|类别级|实例级|条件性|时间限定|地域限定",
    "qualifier": "菌株/版本/条款/地区/时间等限定，无则空串",
    "expected_sources": ["source name or query sketch"],
    "priority": 0.0,
    "rationale": "为什么问它、它服务 goal 的哪一部分"
  }
]
```

---

## 示例

输入：`target=Escherichia coli O157:H7 的致病性`，`goal=判断该菌株在食品检测场景下的风险等级`，`domain=science`（触发 `sub_packs.bacteriology`）。

```json
[
  {"node_id":"Q1","parent_id":null,"question":"E. coli O157:H7 在分类学上归属哪个物种/血清型？命名依据是哪条数据库记录？","question_type":"taxonomy","entity":"E. coli O157:H7","entity_level":"serovar","relation":"is_a","scope":"类别级","qualifier":"按 LPSN 当前有效名","expected_sources":["LPSN","NCBI RefSeq GCF_000008865"],"priority":0.8,"rationale":"定锚：不确认血清型，后面所有致病性结论都可能套错菌株"},
  {"node_id":"Q2","parent_id":null,"question":"该血清型的致病性由哪些毒力要素构成（志贺毒素、LEE 致病岛、黏附素等）？各自定位在染色体还是质粒？","question_type":"element_inventory","entity":"O157:H7","entity_level":"virulence_gene","relation":"part_of","scope":"实例级","qualifier":"限定 O157:H7 代表性菌株","expected_sources":["VFDB","PubMed 综述","NCBI 基因组注释"],"priority":0.9,"rationale":"要素清单是风险判断的直接依据"},
  {"node_id":"Q3","parent_id":null,"question":"'携带毒力基因'是否等同于'具有致病表型'？有哪些反例（基因沉默、假基因、菌株背景差异）？","question_type":"counterexample","entity":"毒力基因","entity_level":"phenotype","relation":"counterexample_to","scope":"条件性","qualifier":"需区分基因存在/表达/表型","expected_sources":["原始研究","VFDB 注释说明"],"priority":0.85,"rationale":"防止把基因组注释直接写成致病结论——本领域最高频错误"},
  {"node_id":"Q4","parent_id":null,"question":"感染剂量、宿主免疫状态与接种途径如何改变该菌株的致病性结论？","question_type":"scope","entity":"致病性","entity_level":"mechanism","relation":"requires","scope":"条件性","qualifier":"ID50 / 宿主 / 途径","expected_sources":["PubMed 暴发调查","WHO/CDC 技术文件"],"priority":0.7,"rationale":"风险等级依赖条件变量，脱离条件谈'高致病'无意义"}
]
```

---

## 反模式

| 反模式 | 为什么坏 | 改成 |
|---|---|---|
| 12 个节点全是"是什么" | 没有机制、没有反例、没有证据层，等于只做了第 1 层 | 按九层铺开 |
| 节点写成一句口号 | 无法检索、无法验证 | 写成可回答的具体问句 |
| `scope` 全填"全局" | 后面必然出现类别→实例的错误外推 | 按实际范围填 |
| 忽略领域包直接按常识规划 | 术语层级错配（把质粒当基因、把款当条） | 先加载 `domain_packs/<domain>.yaml` |
| 把 answer 写进 question | 规划阶段就把结论定了，后面只会找支持证据 | 只写问题，不写答案 |
