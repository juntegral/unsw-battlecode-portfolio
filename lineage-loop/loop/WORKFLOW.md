# 웨이브 안의 다중 에이전트 워크플로우

웨이브 벽시계의 대부분은 로컬 평가 대기다. 사고를 늘리는 것은 싸고, 평가 배치를 늘리는 것은 비싸다. 그래서 워크플로우는 **평가 한 번의 가치를 높이는 세 지점**에서만 쓴다. 평가·기록·finish는 계통 담당(메인 세션)이 직접 한다.

## 세 지점과 판단 규칙
1. **가설 패널** — 관찰·가설 단계에서 구현을 시작하기 전. 관점이 다른 에이전트가 각각 가설을 내고, 다른 에이전트가 원자료로 반박한다. 반박되지 않은 가설만 후보로 구현한다. 전부 반박되면 그 이유를 `NOTES.md`에 남기고 자기 관찰로 돌아간다. 한 웨이브에 한 번, 필요하면 맥락을 바꿔 한 번 더.
2. **구현 검토** — 후보를 처음 평가에 올리기 전, 후보당 한 번. 버그·의도 불일치와 심판 한도 위험을 본다. severity가 high인 문제는 고친 뒤 평가한다.
3. **채택 전 반박** — `check.js` 보고서를 받은 뒤 `finish adopt` 전, 확인당 한 번. 세 관점이 채택 판단을 반박한다. 2개 이상이 반박하면 채택하지 않는다(기각 또는 탐색 계속). 1개 이하면 `GROWTH.md`의 기준으로 스스로 판단하고, 반박 요지와 주의점을 `NOTES.md`에 남긴다.

워크플로우 결과는 판단 재료이지 자동 승격·자동 기각 점수가 아니다. 다른 일(파일 정리, 평가 실행, 기록)에는 워크플로우를 쓰지 않는다.

## 에이전트 규칙
- 읽기·분석·반박만 한다. 경기 실행(`run-job.js`, `check.js`, `unswbc`), 파일 수정·생성, `bot/`·`NOTES.md`·`CURRENT.md` 변경 금지. 계통의 분석 스크립트(리플레이·행 집계)는 실행해도 된다.
- 자기 계통 폴더, `rules/`, `loop/`만 읽는다. 다른 계통과 `bots/` 소스는 읽지 않는다.
- 한 워크플로우에 에이전트 6개 이하, 동시 4개 이하를 목표로 한다(평가 경기와 CPU를 나눠 쓴다).
- 워크플로우를 시작하면 완료 알림이 올 때까지 기다린다. 시작 직후 다른 평가를 걸지 않는다.

## 호출 방법
Workflow 도구에 `script`(아래 틀 중 하나)와 `args`를 준다. `args`는 JSON 객체로 넘긴다(문자열로 감싸지 않는다).

```json
{ "lineage": "g3", "context": "현재 bot/: r3 … 근거: checks/…/report.json … 알려진 약점: … 후보 디렉터리: lineages/g3/c16 … 평가 결과: lineages/g3/exp/eval-c16/rows.jsonl … 분석 도구: lineages/g3/tools/*.js (용도 한 줄씩)" }
```

`context`에는 에이전트가 처음 보는 사람도 바로 원자료를 열 수 있게 **경로를 구체적으로** 적는다: 현재 버전과 근거 보고서, 알려진 약점, 후보 디렉터리와 변경 요지, 평가·확인 결과 경로, 분석 도구 이름과 용도.

## 스크립트 API 요약
- 스크립트는 일반 JavaScript(TypeScript 아님). 첫 줄은 `export const meta = {...}` 순수 리터럴(변수·호출·보간 금지). `name`, `description` 필수, `phases`는 `[{title}]` 배열.
- `agent(prompt, {label, phase, schema})` → 서브에이전트 하나. `schema`(JSON Schema, 루트는 `{type:'object', properties, required}`)를 주면 검증된 객체를 반환. 실패·중단 시 `null`이므로 `.filter(Boolean)`.
- `parallel([() => agent(...), ...])` → 전부 끝날 때까지 기다린 배열. `pipeline(items, stage1, stage2, ...)` → 항목별로 단계를 이어 실행. 단계 콜백은 `(이전 결과, 원래 항목, 색인)`.
- `phase(title)`, `log(message)`, `args`(호출 시 넘긴 값). `Date.now()`, `Math.random()`, `new Date()`는 쓸 수 없다. 파일 시스템 접근도 없다(에이전트가 대신 읽는다).
- 스크립트의 `return` 값이 완료 알림으로 돌아온다.

## 틀 1: 가설 패널
```js
export const meta = {
  name: 'hypothesis-panel',
  description: '독립 관점 4개로 후보 가설을 만들고 반박 심사로 거른다',
  phases: [{ title: '가설' }, { title: '반박' }],
}
const LENSES = [
  '사망·전멸 원인: 최근 평가 원자료에서 사망 직전 몇 라운드를 보고 가장 잦은 사망 유형과 그것을 피하는 규칙 변경',
  '지도·상대·진영별 격차: G·승·생존 분포에서 가장 큰 열세 조건과 그 조건에 특화된 변경',
  '규칙서 미활용: rules/에서 현재 봇이 쓰지 않거나 덜 쓰는 규칙·행동과 그 활용 가설',
  '단순화·제거: 현재 로직에서 근거가 약하거나 비용 대비 효과가 의심스러운 부분의 제거·단순화',
]
const HYP = { type: 'object', properties: { hypotheses: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, change: { type: 'string' }, expected: { type: 'string' }, falsifier: { type: 'string' },
  evidence: { type: 'string' }, risk: { type: 'string' } }, required: ['title', 'change', 'expected', 'falsifier', 'evidence'] } } }, required: ['hypotheses'] }
const VERDICT = { type: 'object', properties: { refuted: { type: 'boolean' }, reason: { type: 'string' }, evidence: { type: 'string' } }, required: ['refuted', 'reason'] }
const common = `${args.context}\n\n규칙: lineages/${args.lineage}/ 안의 CURRENT.md, NOTES.md, 평가 원자료, 분석 도구와 rules/만 읽는다. 경기 실행(run-job.js, check.js, unswbc)과 파일 수정·생성은 금지. 다른 계통과 bots/ 소스는 읽지 않는다.`
const results = await pipeline(LENSES,
  (lens, _, i) => agent(`${common}\n\n관점: ${lens}\n\n이 관점에서 가장 유망한 변경 가설을 1~2개 제시하라. 각 가설에 근거(파일 경로·수치), 좋아질 상황, 나빠질 가능성, 틀렸다면 평가에서 보일 결과(falsifier)를 적는다.`,
    { label: `가설 ${i + 1}`, phase: '가설', schema: HYP }),
  (r, lens) => parallel(((r && r.hypotheses) || []).slice(0, 2).map(h => () =>
    agent(`${common}\n\n다음 가설을 원자료로 반박하라. 반박 근거를 찾으면 refuted=true와 근거, 찾지 못하면 refuted=false와 남는 의문을 적는다. 불확실하면 refuted=true.\n\n${JSON.stringify(h)}`,
      { label: `반박: ${h.title}`, phase: '반박', schema: VERDICT }).then(v => ({ ...h, lens, verdict: v })))),
)
return results.filter(Boolean).flat().filter(Boolean)
```

## 틀 2: 구현 검토
```js
export const meta = {
  name: 'candidate-review',
  description: '후보 구현을 첫 평가 전에 두 관점으로 검토한다',
  phases: [{ title: '검토' }],
}
const LENSES = [
  '의도·버그: bot/와 후보 디렉터리의 차이(diff)를 읽고, 변경이 설명된 의도와 일치하는지, 논리 오류·경계 조건·상태 초기화 누락·의도치 않은 행동 변화가 있는지 본다',
  '심판 한도·프로토콜: rules/judge-limits.md와 rules/의 프로토콜 기준으로 턴당 CPU·메모리·응답 시간 한도를 넘길 수 있는 반복·할당·재귀와 프로토콜 위반 가능성을 본다',
]
const REVIEW = { type: 'object', properties: { ok: { type: 'boolean' }, issues: { type: 'array', items: { type: 'object', properties: {
  where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] } },
  required: ['where', 'problem', 'severity'] } } }, required: ['ok', 'issues'] }
const common = `${args.context}\n\n규칙: 읽기·diff·grep만 한다. 경기 실행과 파일 수정 금지. 다른 계통과 bots/ 소스는 읽지 않는다.`
const reviews = await parallel(LENSES.map((lens, i) => () =>
  agent(`${common}\n\n관점: ${lens}\n\n문제가 없으면 ok=true와 빈 issues. 있으면 위치·문제·고치는 방법·severity를 적는다.`, { label: `검토 ${i + 1}`, phase: '검토', schema: REVIEW })))
return reviews.filter(Boolean)
```

## 틀 3: 채택 전 반박
```js
export const meta = {
  name: 'adoption-refute',
  description: '확인 보고서와 원자료를 독립 관점 3개로 반박한다',
  phases: [{ title: '반박' }],
}
const LENSES = [
  '측정 정직성: 확인 디렉터리의 candidate-results/rows.jsonl과 baseline-results/rows.jsonl에서 승·생존·G·총량을 직접 재계산해 report.json과 대조하고, 오류·누락·중복 행이 있는지 본다',
  '범위·과대주장: 지도·상대·진영별 분할에서 나빠진 조건, 승→패 뒤집힘, 전멸 증가, 총량 감소를 찾아 "전반적으로 더 낫다"는 판단을 반박한다',
  '메커니즘 정합: 변경 의도가 실제 경기 양상으로 나타났는지 리플레이·분석 도구로 확인하고, 개선이 의도한 메커니즘이 아닌 다른 이유(우연·특정 지도)일 가능성을 본다',
]
const VERDICT = { type: 'object', properties: { refuted: { type: 'boolean' }, reason: { type: 'string' }, evidence: { type: 'string' }, caveats: { type: 'string' } }, required: ['refuted', 'reason'] }
const common = `${args.context}\n\n규칙: 확인 디렉터리·원자료·분석 도구만 읽는다. 경기 실행과 파일 수정 금지. 채택을 반박할 근거가 있으면 refuted=true와 근거, 없으면 refuted=false와 채택 시 기록할 주의점(caveats)을 적는다.`
const votes = await parallel(LENSES.map((lens, i) => () =>
  agent(`${common}\n\n관점: ${lens}`, { label: `반박 ${i + 1}`, phase: '반박', schema: VERDICT })))
return votes.filter(Boolean)
```
