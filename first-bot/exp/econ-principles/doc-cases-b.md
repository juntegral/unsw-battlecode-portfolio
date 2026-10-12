**B. 상위권끼리 B3 박치기(E4 기준).** 2단계 분류: 박은 쪽 집단 × 시야 d3 × 반경 8 d8. 부류 크기와 20R 진주 몫은 아래와 같다(`cases.txt`).

{{tbl(['집단', 'd3', 'd8', '부류 크기', '20R 진주 우리 / 상대'], ['W', 'L'].flatMap(rl => ['≥+1', '=0', '≤−1'].flatMap(v => ['≥+1', '≤0'].map(m => { const c = cc(`E4-top ${rl} d3${v} d8${m}`); return [ROLE[rl], v, m, f0(c.n), c.own !== null ? `${c.own}% / ${c.opp}%` : '–']; }))))}}

{{film("b")}}
