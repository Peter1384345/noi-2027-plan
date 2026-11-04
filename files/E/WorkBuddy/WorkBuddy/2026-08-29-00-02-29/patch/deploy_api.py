# -*- coding: utf-8 -*-
"""不克隆仓库，直接用 GitHub REST API 提交改动、开 PR 并合并。

改动文件：
  - index.html        (新增 4 个可视化板块 + CSS + 导航)
  - assets/charts.js  (新增 5 个 ECharts 图表实例)
"""
import base64
import io
import json
import os
import subprocess
import sys
import tempfile

GH = r"C:\Users\Administrator\.workbuddy\binaries\gh\bin\gh.exe"
OWNER = "Peter1384345"
REPO = "dragon-raja-story"
BASE = r"C:\Users\Administrator\WorkBuddy\2026-08-29-00-02-29"
SRC = os.path.join(BASE, "dragon-raja-story")

BRANCH = "feat/atlas-visualization"
FILES = ["index.html", os.path.join("assets", "charts.js")]


def gh_api(method, endpoint, payload=None):
    """调用 gh api，返回解析后的 JSON。"""
    cmd = [GH, "api", "--method", method, endpoint]
    tmp = None
    if payload is not None:
        fd, tmp = tempfile.mkstemp(suffix=".json", prefix="ghapi_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        cmd += ["--input", tmp]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
    if p.returncode != 0:
        sys.stderr.write("GH API FAILED: %s %s\n%s\n%s\n" % (method, endpoint, p.stdout, p.stderr))
        sys.exit(1)
    out = (p.stdout or "").strip()
    if not out:
        return {}
    try:
        return json.loads(out)
    except ValueError:
        return {"_raw": out}


def main():
    # 1) main 分支 HEAD
    ref = gh_api("GET", "/repos/%s/%s/git/ref/heads/main" % (OWNER, REPO))
    base_sha = ref["object"]["sha"]
    print("[1] main HEAD = %s" % base_sha[:12])

    # 2) 创建特性分支
    try:
        gh_api("POST", "/repos/%s/%s/git/refs" % (OWNER, REPO),
               {"ref": "refs/heads/" + BRANCH, "sha": base_sha})
        print("[2] branch created: %s" % BRANCH)
    except SystemExit:
        print("[2] branch may already exist, fetching it")
        r = gh_api("GET", "/repos/%s/%s/git/ref/heads/%s" % (OWNER, REPO, BRANCH))
        base_sha = r["object"]["sha"]
        print("    existing branch head = %s" % base_sha[:12])

    # 3) 为每个改动文件创建 blob
    tree_entries = []
    for rel in FILES:
        path = os.path.join(SRC, rel)
        with io.open(path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode("ascii")
        blob = gh_api("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
                      {"content": b64, "encoding": "base64"})
        tree_entries.append({
            "path": rel.replace("\\", "/"),
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })
        print("[3] blob %-22s %8d bytes -> %s" % (rel, len(raw), blob["sha"][:12]))

    # 4) 建 tree
    tree = gh_api("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO),
                  {"base_tree": base_sha, "tree": tree_entries})
    print("[4] tree = %s" % tree["sha"][:12])

    # 5) 提交
    msg = ("feat: 新增龙族 Atlas 可视化增强模块\n\n"
           "- 角色战力对比：六维雷达图，支持最多 5 人同屏对比\n"
           "- 卷次剧情强度：五卷要素堆叠柱 + 牺牲/烈度双轴图\n"
           "- 龙王血脉谱系：黑王至四大君主的可交互谱系树\n"
           "- 阵营与命运流向：阵营→角色→归宿 桑基图\n\n"
           "沿用现有深色龙族风格变量与 ECharts 5.5，共 20 个板块。")
    commit = gh_api("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
                    {"message": msg, "tree": tree["sha"], "parents": [base_sha]})
    print("[5] commit = %s" % commit["sha"][:12])

    # 6) 更新分支引用
    gh_api("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (OWNER, REPO, BRANCH),
           {"sha": commit["sha"], "force": True})
    print("[6] branch updated -> %s" % commit["sha"][:12])

    # 7) 开 PR
    pr_body = ("在原站点基础上新增 4 个交互式可视化板块，沿用现有深色龙族视觉风格与 ECharts 5.5。\n\n"
               "### 新增板块\n"
               "| 板块 | 图表类型 | 说明 |\n"
               "| --- | --- | --- |\n"
               "| 角色战力对比 | Radar | 六维能力模型（血统/体术/言灵/武器/谋略/意志），12 位角色可选，最多 5 人同屏对比，带综合评分读数 |\n"
               "| 卷次剧情强度 | Bar(stack) + Bar/Line | 五卷的新增角色、重大战役、言灵登场、龙王觉醒堆叠分布；牺牲人数与综合烈度指数双轴走势 |\n"
               "| 龙王血脉谱系 | Tree | 黑王尼德霍格 → 白王与四大君主 → 孪生共治与人间代理，支持展开/收起、悬停查看权能 |\n"
               "| 阵营与命运流向 | Sankey | 7 大阵营 → 29 位角色 → 5 类归宿的流向分布 |\n\n"
               "### 改动文件\n"
               "- `index.html`：新增 CSS、4 个 section、4 个导航项（板块 16 → 20）\n"
               "- `assets/charts.js`：新增 5 个 ECharts 实例（雷达 / 堆叠柱 / 双轴 / 树 / 桑基）\n\n"
               "### 验证\n"
               "本地 Chromium 冒烟测试：6 个图表容器全部渲染成功，控制台零错误，导航项 20 个与板块一一对应。")
    pr = gh_api("POST", "/repos/%s/%s/pulls" % (OWNER, REPO), {
        "title": "feat: 龙族 Atlas 可视化增强（战力雷达 / 卷次强度 / 龙王谱系 / 命运流向）",
        "head": BRANCH,
        "base": "main",
        "body": pr_body,
    })
    number = pr["number"]
    print("[7] PR #%s -> %s" % (number, pr.get("html_url", "")))

    # 8) 合并
    merged = gh_api("PUT", "/repos/%s/%s/pulls/%d/merge" % (OWNER, REPO, number), {
        "commit_title": "feat: 龙族 Atlas 可视化增强（战力雷达 / 卷次强度 / 龙王谱系 / 命运流向）",
        "merge_method": "merge",
    })
    print("[8] merged = %s  sha = %s" % (merged.get("merged"), str(merged.get("sha"))[:12]))
    print("DONE")


if __name__ == "__main__":
    main()
