#!/usr/bin/env python3
"""
GitHub Trending - 数据抓取脚本

职责：从 GitHub API 抓取热门仓库数据，生成 JSON 文件。
HTML 页面是固定的主题模板（index.html），不由此脚本生成。

用法:
  python3 main.py              # 抓取新数据，生成新一期 JSON
  python3 main.py --token XXX  # 使用 GitHub Token（提高速率限制）
  python3 main.py --env-token  # 从 GITHUB_TOKEN 环境变量读取 Token
"""
import json
import os
import sys
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SITE_NAME, CYCLE_DAYS, DATA_DIR, CATEGORIES
from fetcher import fetch_all_categories


# ==================== JSON 存储函数 ====================

def load_issues_index():
    """读取期数索引 issues.json，不存在则返回空列表"""
    path = os.path.join(DATA_DIR, "issues.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("issues", [])


def save_issue_data(issue_id, issue_data):
    """保存单期数据为 issue-N.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"issue-{issue_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(issue_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 数据已保存: data/issue-{issue_id}.json ({os.path.getsize(path) / 1024:.1f} KB)")


def save_issues_index(issues_list):
    """更新期数索引 issues.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    latest = max((iss["id"] for iss in issues_list), default=0)
    data = {
        "issues": issues_list,
        "latestIssue": latest,
    }
    path = os.path.join(DATA_DIR, "issues.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 索引已更新: data/issues.json (共 {len(issues_list)} 期, 最新第 {latest} 期)")


# ==================== 核心逻辑 ====================

def get_next_issue_id(issues_list):
    """获取下一期的 ID"""
    if not issues_list:
        return 1
    return max(iss["id"] for iss in issues_list) + 1


def get_date_range():
    """获取当前期的日期范围（今天 ~ 今天+CYCLE_DAYS-1）"""
    today = datetime.now()
    end = today + timedelta(days=CYCLE_DAYS - 1)
    return today.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_and_save(token=None):
    """抓取数据并保存为 JSON"""
    issues_list = load_issues_index()

    issue_id = get_next_issue_id(issues_list)
    start_date, end_date = get_date_range()
    generated_at = datetime.now().isoformat()

    print(f"\n>>> 正在生成第 {issue_id} 期")
    print(f">>> 日期范围: {start_date} ~ {end_date}")
    print()

    # 抓取数据
    categories_data = fetch_all_categories(token=token)

    # 构建期数数据
    issue_data = {
        "id": issue_id,
        "title": f"第{issue_id}期",
        "start_date": start_date,
        "end_date": end_date,
        "generated_at": generated_at,
        "categories": categories_data,
    }

    # 保存单期数据
    save_issue_data(issue_id, issue_data)

    # 更新索引
    total_repos = sum(len(c["repos"]) for c in categories_data)
    issues_list.append({
        "id": issue_id,
        "title": f"第{issue_id}期",
        "start_date": start_date,
        "end_date": end_date,
        "generated_at": generated_at,
        "total_repos": total_repos,
    })
    save_issues_index(issues_list)

    print(f"\n{'=' * 50}")
    print(f"  第 {issue_id} 期完成!")
    print(f"  分类: {len(categories_data)} 个")
    print(f"  仓库: {total_repos} 个")
    print(f"  日期: {start_date} ~ {end_date}")
    print(f"{'=' * 50}")

    return issue_id


# ==================== 入口 ====================

def main():
    parser = argparse.ArgumentParser(description=f"{SITE_NAME} - 数据抓取脚本")
    parser.add_argument("--token", type=str, default=None, help="GitHub API Token（可选，提高速率限制）")
    parser.add_argument("--env-token", action="store_true", help="从 GITHUB_TOKEN 环境变量读取 Token")
    args = parser.parse_args()

    token = args.token
    if args.env_token:
        token = os.environ.get("GITHUB_TOKEN", None)

    print(f"\n{'=' * 50}")
    print(f"  {SITE_NAME}")
    print(f"  数据抓取脚本 (仅生成 JSON, HTML 页面固定不变)")
    print(f"{'=' * 50}")

    fetch_and_save(token=token)


if __name__ == "__main__":
    main()
