# 验证手册

按实际完成的最高等级报告，不许跳级表述。

## Level 1：结构校验（必做）

```bash
python3 <skill目录>/scripts/verify_handbook.py <手册.html>
```

检查清单：两个 script 块 JS 语法（有 node 时 `node --check`）；章节 id 唯一；CONCEPTS 的 `ch`/`rel` 与 `data-c`/`data-go`/QUIZ·MISCONCEPTIONS 的 `goto` 全部指向真实目标；`#nav` `#drawer` `#graphSvg` `#glossList` `#quizList` 容器存在；`mark-read` 的 data-read 与章节对应；六分组 chips 与 GROUP_NAMES 一致；术语 ≥10（正式手册建议 ≥25）；无遗留 `【】` 占位（骨架自检用 `--allow-placeholder`）。

输出全 PASS 才算通过。FAIL 会打印具体死链，修复后重跑。

## Level 2：行为冒烟（推荐，环境有 browser-use 时）

```bash
cd <手册所在目录> && python3 -m http.server <端口> --bind 127.0.0.1
```

然后在 browser-use 的 js 调用里：bootstrap → `getForUrl("http://127.0.0.1:<端口>/")` → 打开文件 → `waitForLoadState` → 执行下面的走查：

```js
const r = await tab.playwright.evaluate(() => {
  const r = {};
  const q = (sel) => { const el = document.querySelector(sel); return el ? (el.click(), true) : false; };
  r.navItems   = document.querySelectorAll('.nav-item').length;
  r.concepts   = Object.keys(CONCEPTS).length;
  r.terms      = document.querySelectorAll('.term').length;   // 自动链接数，应 > 0
  r.welcomeOff = q('#startBtn');
  r.drawerOpen = q('.term') && document.querySelector('#drawer').classList.contains('on');
  r.drawerName = document.querySelector('#dName')?.textContent;
  r.closed     = q('#drawerX');
  r.markRead   = !!document.querySelector('.mark-read') && q('.mark-read');
  r.progress   = document.querySelector('#progText')?.textContent;  // 应 > 0%
  r.graphNodes = document.querySelectorAll('#graphSvg .gnode').length; // 应 = concepts 数
  r.quizN      = document.querySelectorAll('.q').length;              // 应 = QUIZ 数
  return r;
});
```

期望：navItems = 章节数；terms > 0；drawerOpen = true 且 drawerName 非空；progress ≠ 0%；graphNodes = 术语数；quizN = 题数。任何一项不符，先看是否误删了渲染容器或改坏了逻辑区。

## 等级表述

- 只跑了 Level 1 → 「结构校验通过，行为尚未验证」。
- Level 1 + 2 → 「结构校验与行为冒烟通过」。
- 不要宣称留出/回归验证，除非确实用未见过的主题样本完整生成并通过两级验证。
