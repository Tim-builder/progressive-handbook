# progressive-handbook · 点读手册生成器

把一个主题或本地知识库制作成**渐进披露式交互知识手册**（俗称：点读手册、P社手册）——单文件离线 HTML，读者顺序读章节，遇到不懂的词点开即有解释，读完可自测。

## 核心特性

- **章节化导航**：线性主线 + 侧边目录，防迷航
- **术语二级窗口**：点词滑出解释侧板，可层层跳转（嵌套提示）
- **概念图谱**：可视化结构地图
- **术语速查表** + **自测题** + **阅读进度**追踪
- **单文件离线可用**：一个 HTML 走到哪读到哪

## 安装

```bash
npx skills add Tim-builder/progressive-handbook
```

## 使用

对 Agent 说：

> 帮我把「布迪厄」知识库做成一本点读手册

或：

> 把这套课程做成渐进披露式的交互学习页

Agent 会按 `SKILL.md` 的流程执行，产出路径为 `<工作区>/<主题名>知识手册/<主题名>知识手册.html`。

## 仓库结构

```
SKILL.md                     # 主流程：模式谱系、设计不变量、制作步骤
references/content-design.md # 内容设计规范
references/verification.md   # 交付前验证清单
scripts/verify_handbook.py   # HTML 结构自动检查脚本
assets/handbook-skeleton.html# 单文件手册骨架模板
agents/openai.yaml           # Agent 配置
```

## 背景

点词展开的形态是三个旧事物的合流：超文本联想跳转（Memex / hypertext）、游戏内百科（1991 年《文明》的 Civilopedia）、情境提示（tooltip）。Paradox 在 CK2/EU4 时期把它打磨成标志性的 nested tooltips，故得俗名「P社手册」。教育技术研究（lost in hyperspace 系列）早已指出纯非线性超文本会让读者迷航，本格式的双结构——线性章节主线 + 术语抽屉 + 概念图谱——正是文献给出的解方。
