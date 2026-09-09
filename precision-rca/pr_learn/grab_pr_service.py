# -*- coding: utf-8 -*-
# 后台抓取服务：三类 PR（已合入/待合入/拒绝合入）各抓 1 个，完成后自动退出
import json
import logging
import os
import urllib.request
from datetime import datetime

BASE = "https://api.github.com/repos/vllm-project/vllm-ascend"
TOKEN = "<YOUR_GITHUB_PAT>"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT = os.path.join(OUT_DIR, "pr_grab_result.json")
LOG = os.path.join(OUT_DIR, "grab_pr.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.FileHandler(LOG, encoding="utf-8")],
)
log = logging.getLogger("pr-grabber")


def api(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "pr-grabber",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def brief(pr: dict) -> dict:
    return {
        "number": pr["number"],
        "title": pr["title"],
        "url": pr["html_url"],
        "state": pr["state"],
        "merged": bool(pr.get("merged_at")),
        "created_at": pr["created_at"],
        "closed_at": pr.get("closed_at"),
        "merged_at": pr.get("merged_at"),
    }


def main() -> None:
    log.info("服务启动，开始抓取三类 PR（每类 1 个）")
    result = {"grab_time": datetime.now().isoformat(), "merged": None, "open": None, "rejected": None}

    # 1+3: closed 列表里区分 merged / closed-unmerged
    closed = api(f"{BASE}/pulls?state=closed&sort=updated&direction=desc&per_page=50")
    merged = next((brief(p) for p in closed if p.get("merged_at")), None)
    rejected = next((brief(p) for p in closed if not p.get("merged_at")), None)
    result["merged"] = merged
    result["rejected"] = rejected
    log.info("已合入: PR#%s | 拒绝合入: PR#%s",
             merged["number"] if merged else "-", rejected["number"] if rejected else "-")

    # 2: open 最新 1 个
    opened = api(f"{BASE}/pulls?state=open&sort=created&direction=desc&per_page=1")
    result["open"] = brief(opened[0]) if opened else None
    log.info("待合入: PR#%s", result["open"]["number"] if result["open"] else "-")

    with open(RESULT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    log.info("结果已写入 %s，服务退出", RESULT)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("抓取失败: %s", e, exc_info=True)
