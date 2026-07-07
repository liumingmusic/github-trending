"""
GitHub Trending - 配置文件
定义站点信息、分类、抓取规则等
"""
from datetime import timedelta

# ==================== 站点配置 ====================
SITE_NAME = "GitHub Trending"
SITE_SUBTITLE = "热门开源项目 . 按分类展示 . 每三天更新"
SITE_DESCRIPTION = "自动抓取 GitHub 热门仓库，按分类排版展示，每三天更新一期"

# ==================== 抓取周期 ====================
CYCLE_DAYS = 3  # 每三天为一个抓取周期
REPOS_PER_CATEGORY_MIN = 15  # 每个分类最少展示的仓库数
REPOS_PER_CATEGORY_MAX = 35  # 每个分类最多展示的仓库数

# ==================== GitHub API 配置 ====================
GITHUB_API_BASE = "https://api.github.com/search/repositories"
GITHUB_API_DELAY = 8  # 请求间隔（秒），避免触发速率限制
GITHUB_USER_AGENT = "GitHub-Trending-Generator/1.0"

# ==================== 多维度抓取配置 ====================
# 维度1：经典热门 — 长期高星项目，按 stars 排序
CLASSIC_DAYS = 365        # 最近 N 天内有更新
CLASSIC_RATIO = 0.35      # 占该分类目标数量的比例

# 维度2：近期新星 — 最近创建但增长快的项目，按 stars 排序
RISING_DAYS = 90          # 最近 N 天内创建的仓库
RISING_RATIO = 0.35       # 占比

# 维度3：近期活跃 — 最近有密集开发的项目，按 updated 排序
ACTIVE_DAYS = 7           # 最近 N 天内有 push
ACTIVE_RATIO = 0.30       # 占比（剩余部分自动补齐）

# ==================== 分类配置 ====================
# 每个分类定义：id, 名称, 图标, 主题色, 搜索查询
CATEGORIES = [
    {
        "id": "frontend",
        "name": "前端",
        "icon": "🎨",
        "color": "#61DAFB",
        "query": "topic:frontend stars:>2000",
    },
    {
        "id": "backend",
        "name": "后端",
        "icon": "⚙️",
        "color": "#3776AB",
        "query": "topic:backend stars:>2000",
    },
    {
        "id": "database",
        "name": "数据库",
        "icon": "🗄️",
        "color": "#336791",
        "query": "topic:database stars:>1000",
    },
    {
        "id": "ai",
        "name": "人工智能",
        "icon": "🤖",
        "color": "#FF6F00",
        "query": "topic:machine-learning stars:>2000",
    },
    {
        "id": "tools",
        "name": "工具类",
        "icon": "🔧",
        "color": "#F05138",
        "query": "topic:developer-tools stars:>800",
    },
    {
        "id": "android",
        "name": "Android",
        "icon": "📱",
        "color": "#3DDC84",
        "query": "topic:android stars:>2000",
    },
    {
        "id": "ios",
        "name": "iOS",
        "icon": "🍎",
        "color": "#A97BFF",
        "query": "topic:ios stars:>1000",
    },
    {
        "id": "devops",
        "name": "DevOps",
        "icon": "🚀",
        "color": "#00ADD8",
        "query": "topic:devops stars:>500",
    },
    {
        "id": "data-science",
        "name": "数据科学",
        "icon": "📊",
        "color": "#4CAF50",
        "query": "topic:data-science stars:>800",
    },
    {
        "id": "blockchain",
        "name": "区块链",
        "icon": "⛓️",
        "color": "#F7931A",
        "query": "topic:blockchain stars:>500",
    },
    {
        "id": "cli",
        "name": "命令行工具",
        "icon": "⌨️",
        "color": "#4EAA25",
        "query": "topic:cli stars:>400",
    },
    {
        "id": "ui-components",
        "name": "UI 组件库",
        "icon": "🧩",
        "color": "#06B6D4",
        "query": "topic:ui-components stars:>300",
    },
    {
        "id": "iot",
        "name": "物联网",
        "icon": "🔌",
        "color": "#009688",
        "query": "topic:iot stars:>300",
    },
    {
        "id": "data-viz",
        "name": "数据可视化",
        "icon": "📈",
        "color": "#FF9800",
        "query": "topic:data-visualization stars:>400",
    },
    {
        "id": "llm",
        "name": "大模型",
        "icon": "🧠",
        "color": "#7C3AED",
        "query": "topic:llm stars:>800",
    },
    {
        "id": "agent",
        "name": "AI Agent",
        "icon": "🤖",
        "color": "#EC4899",
        "query": "topic:ai-agents stars:>200",
    },
]

# ==================== 路径配置 ====================
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
