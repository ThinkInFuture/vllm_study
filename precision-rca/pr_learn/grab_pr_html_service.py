# -*- coding: utf-8 -*-
# 后台服务第二阶段：抓取三类 PR 的网页 HTML，每类 1 个，完成后自动退出
import json
import logging
import os
import time
import urllib.request
from datetime import datetime

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT = os.path.join(OUT_DIR, "pr_grab_result.json")
LOG = os.path.join(OUT_DIR, "grab_pr_html.log")
TOKEN = "<YOUR_GITHUB_PAT>"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.FileHandler(LOG, encoding="utf-8")],
)
log = logging.getLogger("pr-html-grabber")


def fetch_html(url: str, out_path: str) -> bool:
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {TOKEN}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "text/html",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(out_path, "wb") as f:
                f.write(data)
            log.info("抓取成功 %s -> %s (%d bytes)", url, os.path.basename(out_path), len(data))
            return True
        except Exception as e:
            log.warning("第 %d 次抓取 %s 失败: %s", attempt, url, e)
            time.sleep(3)
    log.error("放弃 %s（重试 3 次均失败）", url)
    return False


def main() -> None:
    log.info("HTML 抓取服务启动")
    result = json.load(open(RESULT, encoding="utf-8"))
    summary = {}
    for cat in ("merged", "open", "rejected"):
        pr = result.get(cat)
        if not pr:
            continue
        n = pr["number"]
        out = os.path.join(OUT_DIR, f"pr_{cat}_{n}.html")
        ok = fetch_html(pr["url"], out)
        summary[cat] = {"number": n, "file": os.path.basename(out), "ok": ok,
                        "size": os.path.getsize(out) if os.path.exists(out) else 0}
        log.info("[%s] PR#%s %s", cat, n, "完成" if ok else "失败")
    out2 = os.path.join(OUT_DIR, "pr_html_manifest.json")
    with open(out2, "w", encoding="utf-8") as f:
        json.dump({"grab_time": datetime.now().isoformat(), "files": summary}, f, ensure_ascii=False, indent=1)
    log.info("清单已写入 %s，服务退出", out2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("服务异常退出: %s", e, exc_info=True)
