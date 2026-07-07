"""
GitHub Trending - 数据抓取器
从 GitHub Search API 多维度获取各分类下的热门仓库

三个维度：
  1. 经典热门 — 按 stars 排序，长期高星项目
  2. 近期新星 — 最近 N 天内创建的高星项目，增长快
  3. 近期活跃 — 最近有 push 的热门项目，正在活跃开发
合并去重后输出，优先放新星和活跃的（每期有变化），经典热门补充。
"""
import json
import os
import time
import random
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

from config import (
    GITHUB_API_BASE,
    GITHUB_API_DELAY,
    GITHUB_USER_AGENT,
    REPOS_PER_CATEGORY_MIN,
    REPOS_PER_CATEGORY_MAX,
    CLASSIC_DAYS,
    CLASSIC_RATIO,
    RISING_DAYS,
    RISING_RATIO,
    ACTIVE_DAYS,
    CATEGORIES,
)


def _build_headers(token=None):
    """构建请求头"""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": GITHUB_USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def search_repos(query, sort="stars", order="desc", per_page=15, token=None):
    """
    调用 GitHub Search API 搜索仓库
    query 已包含完整搜索条件（含日期过滤），返回原始 items 列表
    """
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": min(per_page, 100),
    }
    url = f"{GITHUB_API_BASE}?{urllib.parse.urlencode(params)}"
    headers = _build_headers(token)

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("items", [])
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  [警告] 触发速率限制，等待 30 秒后重试...")
            time.sleep(30)
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))
                return data.get("items", [])
            except Exception as e2:
                print(f"  [错误] 重试失败: {e2}")
                return []
        else:
            print(f"  [错误] HTTP {e.code}: {e.reason}")
            return []
    except Exception as e:
        print(f"  [错误] 请求失败: {e}")
        return []


def extract_repo_info(repo):
    """从 API 响应中提取需要的字段"""
    return {
        "name": repo.get("name", ""),
        "full_name": repo.get("full_name", ""),
        "description": repo.get("description") or "暂无描述",
        "html_url": repo.get("html_url", ""),
        "stargazers_count": repo.get("stargazers_count", 0),
        "language": repo.get("language") or "Unknown",
        "topics": repo.get("topics", []),
        "owner": repo.get("owner", {}).get("login", ""),
        "owner_avatar": repo.get("owner", {}).get("avatar_url", ""),
        "forks_count": repo.get("forks_count", 0),
        "open_issues_count": repo.get("open_issues_count", 0),
        "updated_at": repo.get("updated_at", ""),
        "created_at": repo.get("created_at", ""),
    }


def _lower_stars_threshold(query, factor=0.25, floor=50):
    """
    降低 query 中的 stars 阈值，用于 rising 维度
    新项目不应和成熟项目用同样的 star 门槛
    例: stars:>2000 → stars:>500, stars:>800 → stars:>200
    """
    def replace(m):
        threshold = int(m.group(1))
        new_threshold = max(int(threshold * factor), floor)
        return f"stars:>{new_threshold}"
    return re.sub(r"stars:>(\d+)", replace, query)


def _fetch_dimension(base_query, dimension, count, token=None):
    """
    抓取单个维度的仓库
    dimension: "classic" | "rising" | "active"
    返回原始 API items 列表
    """
    now = datetime.now()

    if dimension == "classic":
        # 经典热门：按 stars 排序，近期有更新
        date_str = (now - timedelta(days=CLASSIC_DAYS)).strftime("%Y-%m-%d")
        query = f"{base_query} pushed:>{date_str}"
        repos = search_repos(query, sort="stars", per_page=count + 8, token=token)

    elif dimension == "rising":
        # 近期新星：最近 N 天内创建，按 stars 排序
        # 新项目用更低的 star 门槛（原始阈值的 25%，最低 50）
        date_str = (now - timedelta(days=RISING_DAYS)).strftime("%Y-%m-%d")
        lowered_query = _lower_stars_threshold(base_query)
        query = f"{lowered_query} created:>{date_str}"
        repos = search_repos(query, sort="stars", per_page=count + 8, token=token)

    elif dimension == "active":
        # 近期活跃：最近 N 天有 push，按 updated 排序
        date_str = (now - timedelta(days=ACTIVE_DAYS)).strftime("%Y-%m-%d")
        query = f"{base_query} pushed:>{date_str}"
        repos = search_repos(query, sort="updated", per_page=count + 8, token=token)

    else:
        repos = []

    return repos


def fetch_category(category, token=None, request_delay=0):
    """
    多维度抓取单个分类的热门仓库
    合并三个维度的结果，去重后输出
    """
    count = random.randint(REPOS_PER_CATEGORY_MIN, REPOS_PER_CATEGORY_MAX)

    # 按比例分配各维度目标数量
    classic_n = max(int(count * CLASSIC_RATIO), 4)
    rising_n = max(int(count * RISING_RATIO), 4)
    active_n = max(count - classic_n - rising_n, 3)
    # 如果加起来超过 count，削减 classic
    if classic_n + rising_n + active_n > count:
        classic_n = count - rising_n - active_n
        if classic_n < 3:
            classic_n = 3
            rising_n = count - classic_n - active_n

    print(f"  正在抓取 [{category['name']}] (目标 {count} 个: 经典{classic_n} + 新星{rising_n} + 活跃{active_n})")

    base_query = category["query"]
    dim_configs = [
        ("rising", rising_n),
        ("active", active_n),
        ("classic", classic_n),
    ]

    # 合并去重：优先放新星和活跃的（每期变化大），经典热门补充
    seen = set()
    merged = []

    for idx, (dim, dim_count) in enumerate(dim_configs):
        repos = _fetch_dimension(base_query, dim, dim_count, token=token)

        added = 0
        for repo in repos:
            full_name = repo.get("full_name", "")
            if full_name and full_name not in seen:
                seen.add(full_name)
                merged.append(extract_repo_info(repo))
                added += 1
                if added >= dim_count:
                    break

        print(f"    [{dim}] 获取 {len(repos)} 个, 去重后新增 {added} 个")

        # 维度间延迟（避免速率限制），最后一个维度不延迟
        if request_delay > 0 and idx < len(dim_configs) - 1:
            time.sleep(request_delay)

    # 如果合并后不足 count，尝试用经典维度补齐
    if len(merged) < count:
        print(f"    [补充] 当前 {len(merged)} 个不足 {count}，补充经典热门...")
        more = _fetch_dimension(base_query, "classic", count - len(merged) + 5, token=token)
        for repo in more:
            full_name = repo.get("full_name", "")
            if full_name and full_name not in seen:
                seen.add(full_name)
                merged.append(extract_repo_info(repo))
                if len(merged) >= count:
                    break

    result = merged[:count]
    return result


def fetch_all_categories(token=None):
    """
    多维度抓取所有分类的热门仓库
    返回格式: [{ category info, repos: [...] }, ...]
    """
    print("=" * 60)
    print("开始从 GitHub API 多维度抓取数据...")
    print(f"共 {len(CATEGORIES)} 个分类, 每分类 {REPOS_PER_CATEGORY_MIN}-{REPOS_PER_CATEGORY_MAX} 个")
    print(f"维度: 经典热门(>{CLASSIC_DAYS}天更新) + 近期新星({RISING_DAYS}天内创建) + 近期活跃({ACTIVE_DAYS}天内push)")
    print("=" * 60)

    results = []
    total_requests = 0

    for i, category in enumerate(CATEGORIES):
        repos = fetch_category(category, token=token, request_delay=GITHUB_API_DELAY)
        total_requests += 3  # 每个分类3个维度

        results.append({
            "id": category["id"],
            "name": category["name"],
            "icon": category["icon"],
            "color": category["color"],
            "repos": repos,
        })
        print(f"  => [{category['name']}] 最终获取 {len(repos)} 个仓库\n")

        # 分类间延迟
        if i < len(CATEGORIES) - 1:
            time.sleep(GITHUB_API_DELAY)

    total = sum(len(c["repos"]) for c in results)
    print("=" * 60)
    print(f"抓取完成! 共 {total} 个仓库 (约 {total_requests} 次 API 请求)")
    print("=" * 60)

    return results
