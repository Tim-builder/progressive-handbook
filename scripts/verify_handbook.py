#!/usr/bin/env python3
"""交互知识手册结构校验：JS 语法、交叉引用、必需容器、占位符与数量下限。

用法: python3 verify_handbook.py <手册.html> [--allow-placeholder] [--min-concepts N]
全 PASS 退出码 0，否则 1。
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TAG = re.compile(r"<script>(.*?)</script>", re.S)
SECTION = re.compile(r'<section class="chapter" id="([\w-]+)"')
CONCEPT = re.compile(r"^\s{2}(\w+):\{name:", re.M)
CH_FIELD = re.compile(r',ch:"([\w-]+)"')
REL_BLOCK = re.compile(r"rel:\[([^\]]*)\]")
REL_ID = re.compile(r'"(\w+)"')
DATA_C = re.compile(r'data-c="([\w-]+)"')
DATA_GO = re.compile(r'data-go="([\w-]+)"')
QUIZ_GOTO = re.compile(r'goto:"([\w-]+)"')
MARK_READ = re.compile(r'data-read="([\w-]+)"')
PLACEHOLDER = re.compile(r"【[^】]*】")

failures = 0


def fail(msg: str) -> None:
    global failures
    failures += 1
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"PASS  {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--allow-placeholder", action="store_true",
                    help="允许【】占位（仅骨架自检时使用）")
    ap.add_argument("--min-concepts", type=int, default=10)
    args = ap.parse_args()

    path = Path(args.html)
    if not path.is_file():
        print(f"FAIL  文件不存在: {path}")
        return 1
    html = path.read_text(encoding="utf-8")

    scripts = TAG.findall(html)
    if len(scripts) != 2:
        fail(f"script 块数量应为 2（概念数据 / 数据+逻辑），实际 {len(scripts)}")
        return 1
    concepts_js, logic_js = scripts

    # 1) JS 语法
    if shutil.which("node"):
        for i, js in enumerate((concepts_js, logic_js)):
            tmp = Path(f"/tmp/_hb_check_{i}.js")
            tmp.write_text(js, encoding="utf-8")
            r = subprocess.run(["node", "--check", str(tmp)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                fail(f"JS 块 {i+1} 语法错误: {r.stderr.strip()[:300]}")
            else:
                ok(f"JS 块 {i+1} 语法通过")
            tmp.unlink(missing_ok=True)
    else:
        print("WARN  未安装 node，跳过 JS 语法检查")

    # 2) 章节
    ch_ids = SECTION.findall(html)
    dup = sorted({i for i in ch_ids if ch_ids.count(i) > 1})
    if dup:
        fail(f"章节 id 重复: {dup}")
    for must in ("graph", "glossary", "quiz"):
        if must not in ch_ids:
            fail(f"缺少工具章 id={must}")
    if ch_ids:
        ok(f"章节数 {len(ch_ids)}")

    # 3) CONCEPTS 与引用
    c_ids = CONCEPT.findall(concepts_js)
    if len(c_ids) < args.min_concepts:
        fail(f"术语数 {len(c_ids)} 低于下限 {args.min_concepts}")
    else:
        ok(f"术语数 {len(c_ids)}")

    bad_ch = sorted({c for c in CH_FIELD.findall(concepts_js) if c not in ch_ids})
    if bad_ch:
        fail(f"CONCEPTS.ch 死链: {bad_ch}")
    else:
        ok("CONCEPTS.ch 全部指向真实章节")

    rel_ids: set[str] = set()
    for blk in REL_BLOCK.findall(concepts_js):
        rel_ids.update(REL_ID.findall(blk))
    bad_rel = sorted(r for r in rel_ids if r not in c_ids)
    if bad_rel:
        fail(f"rel 死链: {bad_rel}")
    else:
        ok("rel 全部指向真实概念")

    # 出度 = 该概念自己的 rel 数组长度（建议 ≥3，仅提示）
    weak: list[str] = []
    for m in re.finditer(r"^\s{2}(\w+):\{.*?rel:\[([^\]]*)\]", concepts_js, re.S | re.M):
        cid = m.group(1)
        n = len(REL_ID.findall(m.group(2)))
        if n < 3:
            weak.append(f"{cid}({n})")
    if weak:
        print(f"WARN  rel 少于 3 条的概念: {weak}")

    # 4) 正文死链（排除 script/code/pre 内部，避免把文档示例当引用）
    body_html = TAG.sub("", html)
    body_html = re.sub(r"<code>.*?</code>|<pre>.*?</pre>", "", body_html, flags=re.S)
    bad_dc = sorted(set(DATA_C.findall(body_html)) - set(c_ids))
    if bad_dc:
        fail(f"data-c 死链: {bad_dc}")
    else:
        ok("data-c 全部指向真实概念")
    bad_dg = sorted(set(DATA_GO.findall(body_html)) - set(ch_ids))
    if bad_dg:
        fail(f"data-go 死链: {bad_dg}")
    else:
        ok("data-go 全部指向真实章节")

    # 5) 数据区 goto（QUIZ 与 MISCONCEPTIONS 同在逻辑块）
    gotos = set(QUIZ_GOTO.findall(logic_js))
    bad_goto = sorted(g for g in gotos if g not in ch_ids)
    if bad_goto:
        fail(f"QUIZ/MISCONCEPTIONS goto 死链: {bad_goto}")
    else:
        ok("QUIZ/MISCONCEPTIONS goto 全部有效")

    # 6) 必需容器
    for sel in ('id="nav"', 'id="drawer"', 'id="graphSvg"',
                'id="glossList"', 'id="quizList"', 'class="drawer-scrim"'):
        if sel in html:
            ok(f"容器存在 {sel}")
        else:
            fail(f"缺少容器 {sel}")

    # 7) mark-read 对应章节
    bad_read = sorted(set(MARK_READ.findall(html)) - set(ch_ids))
    if bad_read:
        fail(f"mark-read data-read 死链: {bad_read}")
    else:
        ok("mark-read 与章节对应")

    # 8) 占位符
    if not args.allow_placeholder:
        hits = PLACEHOLDER.findall(html)
        if hits:
            fail(f"遗留占位符 {len(hits)} 处，例如: {hits[:5]}")
        else:
            ok("无遗留占位符")
    else:
        print("SKIP  占位符检查（--allow-placeholder）")

    print("-" * 46)
    if failures:
        print(f"结果：{failures} 项 FAIL")
        return 1
    print("结果：全部 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
