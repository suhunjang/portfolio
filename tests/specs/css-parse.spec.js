// step 13 — tests/helpers/css-parse.js 순수 CSS 파서 (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules, splitSelectors, normalizeValue } from '../helpers/css-parse.js';

const F = 'css/style.css';
const parse = (text) => parseCssRules(text, F);

test.describe('step 13 css-parse', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('단일 Rule 형태', () => {
    expect(parse('.a { color: red; }')).toEqual([
      { file: F, chain: [], selectors: ['.a'], decls: [['color', 'red']], atRule: null, prelude: null, index: 0 },
    ]);
  });

  test('빈 입력은 []', () => {
    expect(parse('')).toEqual([]);
    expect(parse('  \n /* only comment */ \n')).toEqual([]);
  });

  test('주석 안 { } ; 무시', () => {
    const rules = parse('/* .x { color: red; } ; */ .a { /* ; } { */ color: red; /* x:y; */ }');
    expect(rules).toHaveLength(1);
    expect(rules[0].selectors).toEqual(['.a']);
    expect(rules[0].decls).toEqual([['color', 'red']]);
  });

  test('문자열 안 { } ; 보존', () => {
    const rules = parse('.a { content: "a{b};c"; } .b::before { content: \'}\'; color: red }');
    expect(rules).toHaveLength(2);
    expect(rules[0].decls).toEqual([['content', '"a{b};c"']]);
    expect(rules[1].decls).toEqual([['content', "'}'"], ['color', 'red']]);
    expect(rules[1].index).toBe(1);
  });

  test('이스케이프된 따옴표 문자열', () => {
    const rules = parse('.a { content: "x\\"};y"; color: red }');
    expect(rules[0].decls).toEqual([['content', '"x\\"};y"'], ['color', 'red']]);
  });

  test('url() 안 ; 보존', () => {
    const rules = parse('.a { background: url("a;b.png") no-repeat; color: red } .b { background: url(c;d.png) }');
    expect(rules[0].decls).toEqual([['background', 'url("a;b.png") no-repeat'], ['color', 'red']]);
    expect(rules[1].decls).toEqual([['background', 'url(c;d.png)']]);
  });

  test('@media > @supports 중첩 chain 2단계', () => {
    const rules = parse('@media (max-width: 768px) { @supports (display: grid) { .a { gap: 24px } } }');
    expect(rules).toEqual([
      {
        file: F,
        chain: ['@media (max-width: 768px)', '@supports (display: grid)'],
        selectors: ['.a'],
        decls: [['gap', '24px']],
        atRule: null,
        prelude: null,
        index: 0,
      },
    ]);
  });

  test('@layer·@container 재귀, chain 공백 정규화', () => {
    const rules = parse('@layer base {\n  @container   card\n (min-width:  400px) { .a { color: red } } }');
    expect(rules).toHaveLength(1);
    expect(rules[0].chain).toEqual(['@layer base', '@container card (min-width: 400px)']);
  });

  test('index는 중첩 포함 등장 순서', () => {
    const rules = parse('.a{} @media (x){.b{}} .c{}');
    expect(rules.map((r) => [r.selectors, r.index, r.chain])).toEqual([
      [['.a'], 0, []],
      [['.b'], 1, ['@media (x)']],
      [['.c'], 2, []],
    ]);
  });

  test('@import url(x.css);', () => {
    expect(parse('@import url(x.css);')).toEqual([
      { file: F, chain: [], selectors: [], decls: [], atRule: '@import', prelude: 'url(x.css)', index: 0 },
    ]);
  });

  test('@import prelude 정규화와 변형 구분', () => {
    const p = (t) => parse(t)[0].prelude;
    const orig = p('@import url("a.css")  screen and (min-width:   10px);');
    expect(orig).toBe('url("a.css") screen and (min-width: 10px)');
    const urlOnly = p('@import url("b.css")  screen and (min-width:   10px);');
    const condOnly = p('@import url("a.css")  screen and (min-width:   20px);');
    expect(urlOnly).toBe('url("b.css") screen and (min-width: 10px)');
    expect(condOnly).toBe('url("a.css") screen and (min-width: 20px)');
    expect(new Set([orig, urlOnly, condOnly]).size).toBe(3);
    // 문자열·url() 내용은 원문
    expect(p('@import url("a  b.css");')).toBe('url("a  b.css")');
  });

  test('@charset "utf-8";', () => {
    const rules = parse('@charset "utf-8";\n.a { color: red }');
    expect(rules[0]).toEqual({ file: F, chain: [], selectors: [], decls: [], atRule: '@charset', prelude: '"utf-8"', index: 0 });
    expect(rules[1].index).toBe(1);
  });

  test('@font-face는 prelude null·decls 1개', () => {
    expect(parse('@font-face { font-family: X }')).toEqual([
      { file: F, chain: [], selectors: [], decls: [['font-family', 'X']], atRule: '@font-face', prelude: null, index: 0 },
    ]);
  });

  test('선택자 분리: 최상위 쉼표만', () => {
    expect(parse('.a, .b { color: red }')[0].selectors).toEqual(['.a', '.b']);
    expect(parse(':is(.a, .b) .c { color: red }')[0].selectors).toEqual([':is(.a, .b) .c']);
    expect(parse('[data-x="a,b"] { color: red }')[0].selectors).toEqual(['[data-x="a,b"]']);
    expect(splitSelectors('.a ,\n  .b\t>  .c')).toEqual(['.a', '.b > .c']);
    expect(splitSelectors(':is(.a, .b) .c')).toEqual([':is(.a, .b) .c']);
    expect(splitSelectors('[data-x="a,b"]')).toEqual(['[data-x="a,b"]']);
  });

  test('공백·줄바꿈 정규화', () => {
    const rules = parse('.a\n  .b ,\n.c   >\t.d {\n  COLOR :\n   red ;\n  margin:  0\n   auto;\n}');
    expect(rules[0].selectors).toEqual(['.a .b', '.c > .d']);
    expect(rules[0].decls).toEqual([['color', 'red'], ['margin', '0 auto']]);
    expect(normalizeValue('  1px \n solid\t red  ')).toBe('1px solid red');
    expect(normalizeValue('"a   b"  x')).toBe('"a   b" x');
  });

  test('custom property 이름 원문·값 trim', () => {
    const rules = parse(':root { --Main-Color:   #ABC  ; --x:  1px  2px }');
    expect(rules[0].decls).toEqual([['--Main-Color', '#ABC'], ['--x', '1px 2px']]);
  });

  test('!important 유지', () => {
    expect(parse('.a { color: red !important }')[0].decls).toEqual([['color', 'red !important']]);
  });

  test('같은 선택자 두 번은 index 구분', () => {
    const rules = parse('.a { color: red } .a { color: blue }');
    expect(rules.map((r) => r.index)).toEqual([0, 1]);
    expect(rules[0].selectors).toEqual(rules[1].selectors);
  });

  test('반복 선언 순서 유지', () => {
    expect(parse('.a{color:red;color:blue}')[0].decls).toEqual([['color', 'red'], ['color', 'blue']]);
  });

  test('@keyframes 안 규칙도 Rule', () => {
    const rules = parse('@keyframes blink { 50% { opacity: 0; } }');
    expect(rules).toHaveLength(1);
    expect(rules[0].chain).toEqual(['@keyframes blink']);
    expect(rules[0].selectors).toEqual(['50%']);
  });

  test('입력 불변', () => {
    const text = '@media (x) { .a, .b { color: red; } }\n@import url("a.css");';
    const copy = `${text}`;
    const file = 'css/themes.css';
    const rules = parseCssRules(text, file);
    expect(text).toBe(copy);
    expect(file).toBe('css/themes.css');
    expect(rules.every((r) => r.file === 'css/themes.css')).toBe(true);
    // 두 번 파싱해도 같은 결과
    expect(parseCssRules(text, file)).toEqual(rules);
  });
});
