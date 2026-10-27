# Question Generator｜缺口追问器

**作用**：**只根据"信息缺口"**生成下一层问题。不是"再多问几个"，而是"把当前答案里明确缺失的那块补上"。

**为什么这是内核而不是锦上添花**：开放式追问会指数膨胀。缺口驱动把"追问"约束成"补洞"，于是每一问都有验收标准——缺口闭合即停。这是"求根问底"与"不停追问"的实际分界。

**输入**：当前节点（question / answer / confidence / gaps / scope / entity_level）、领域包、剩余预算。

**输出**：≤5 条子问题，JSON。

---

## 生成规则

1. **一条缺口 → 一条问题**。每条必须写 `gap_reason`，格式："答案中缺少 ⟨具体要素⟩，导致 ⟨哪个结论⟩ 不能成立/无法定界"。
2. **必须可回答**：`expected_source` 要具体到"哪个库、搜什么"。写不出就转 `needs_human`。
3. **必须非重复**：先用去重键 `question_type | entity | relation | scope | qualifier` 比对已问节点。语义相同、只换措辞的一律丢弃。
4. **必须指向明确实体层级**：`entity_level` 取自领域包。层级不明的问题会产出层级混乱的结论。
5. **最多 5 条**。按 `priority` 排序，其余记入 `deferred`（不是删除，是排队）。
6. **三类缺口要分开处理**：

| 缺口类型 | 处理 |
|---|---|
| 可检索缺口（有源可查） | 生成子问题，正常递归 |
| 需实验/需内部数据 | `status: needs_human`，停止追问该支，写入报告"未解问题" |
| 概念/歧义缺口 | 先消歧，不检索；消歧不了就声明假设 |

7. **不要为"显得深入"而问**。若某缺口闭合后不影响任何结论，直接丢弃。

---

## 输出格式

```json
{
  "parent_node": "Q3",
  "questions": [
    {
      "question": "……",
      "gap_reason": "答案缺少 ⟨要素⟩，导致 ⟨结论⟩ 无法定界",
      "question_type": "……",
      "entity": "……",
      "entity_level": "……",
      "relation": "……",
      "scope": "……",
      "qualifier": "……",
      "expected_source": "具体库/检索词",
      "priority": 0.0,
      "dedupe_key": "question_type|entity|relation|scope|qualifier"
    }
  ],
  "needs_human": [
    {"gap": "……", "why_not_retrievable": "需实验/需内部数据/需专家判断"}
  ],
  "deferred": [
    {"question": "……", "reason": "本轮预算不足，非必需"}
  ]
}
```

---

## 示例

当前节点 Q3 答案："O157:H7 携带 stx1/stx2、LEE 致病岛，多数暴发株产志贺毒素。" `confidence=0.7`，`gaps=["未确认 stx 基因是否表达","未区分菌株背景"]`。

```json
{
  "parent_node": "Q3",
  "questions": [
    {
      "question": "在 O157:H7 中，stx1/stx2 的表达受什么调控？溶原诱导是否是产毒的必要条件？",
      "gap_reason": "答案缺少'基因→表达'这一环，导致'携带 stx'被直接读成'产毒'",
      "question_type": "regulation",
      "entity": "stx1/stx2",
      "entity_level": "virulence_gene",
      "relation": "regulates",
      "scope": "实例级",
      "qualifier": "O157:H7 溶原状态",
      "expected_source": "PubMed: 'Shiga toxin expression regulation lambdoid prophage induction'",
      "priority": 0.8,
      "dedupe_key": "regulation|stx1/stx2|regulates|实例级|O157:H7 溶原状态"
    },
    {
      "question": "是否存在携带 stx 但不产毒、且无致病表型的 O157:H7 分离株？",
      "gap_reason": "答案缺少反例，导致'该血清型致病'的范围未被检验",
      "question_type": "counterexample",
      "entity": "O157:H7",
      "entity_level": "strain",
      "relation": "counterexample_to",
      "scope": "实例级",
      "qualifier": "临床/环境分离株对比",
      "expected_source": "PubMed 比较基因组/表型研究",
      "priority": 0.75,
      "dedupe_key": "counterexample|O157:H7|counterexample_to|实例级|临床/环境分离株对比"
    }
  ],
  "needs_human": [
    {"gap": "本实验室样本的实际产毒量", "why_not_retrievable": "需实验测定（Vero 细胞毒性试验）"}
  ],
  "deferred": [
    {"question": "stx 亚型（stx2a/2c）与疾病严重度的剂量效应", "reason": "不影响当前风险分级，预算优先给反例"}
  ]
}
```

---

## 反模式

| 反模式 | 为什么坏 |
|---|---|
| 每轮都生成"还有哪些方面需要考虑" | 无法验收，永远闭合不了 |
| 把 `needs_human` 硬变成检索问题 | 产生噪音证据，污染证据链 |
| 子问题与原问题同义 | 重复追问，浪费预算 |
| 一次生成 10+ 条 | 预算被平均稀释，高价值节点展开不足 |
| 没有 `gap_reason` | 无法判断这一问是否必要，停止条件失效 |
