# GitHub Trending

自动抓取 GitHub 热门仓库，按分类排版展示，每三天更新一期。

## 架构

```
github-trending/
├── index.html          # 固定的主题页面（部署一次，永不变）
├── data/
│   ├── issues.json     # 期数索引（列出所有期数）
│   ├── issue-1.json    # 第1期数据
│   ├── issue-2.json    # 第2期数据
│   └── ...
├── config.py           # 分类配置、站点设置
├── fetcher.py          # GitHub API 数据抓取
└── main.py             # 入口脚本（仅生成 JSON）
```

**核心设计**：HTML 页面与数据完全解耦。

- `index.html` 是固定的前端主题页面，通过 `fetch` 加载 `data/` 目录下的 JSON 文件
- 每次抓取只生成新的 `issue-N.json` 并更新 `issues.json` 索引
- 页面切换期数时，动态加载对应的 JSON 数据

## 部署到 GitHub Pages

1. 将整个 `github-trending/` 目录推送到 GitHub 仓库
2. 在仓库 Settings → Pages，选择分支和根目录
3. 访问 `https://<username>.github.io/<repo>/` 即可

部署完成后，后续只需更新 `data/` 目录下的 JSON 文件，页面无需重新部署。

## 数据抓取

```bash
# 抓取新数据（生成新一期 JSON）
python3 main.py

# 使用 GitHub Token 提高速率限制
python3 main.py --token ghp_xxxxx
# 或
GITHUB_TOKEN=ghp_xxxxx python3 main.py --env-token
```

已配置每三天自动抓取的定时任务，自动生成新 JSON 数据。

## 分类

| 分类 | 图标 | 说明 |
|------|------|------|
| 前端 | 🎨 | React、Vue、Vite 等 |
| 后端 | ⚙️ | PocketBase、Appwrite 等 |
| 数据库 | 🗄️ | Supabase、Netdata 等 |
| 人工智能 | 🤖 | TensorFlow、LLM 相关 |
| 工具类 | 🔧 | 开发者工具 |
| Android | 📱 | Flutter、scrcpy 等 |
| iOS | 🍎 | Flutter、React Native 等 |
| DevOps | 🚀 | 监控、CI/CD 工具 |

## 技术栈

- 纯原生 HTML/CSS/JS，无框架依赖
- 响应式设计，支持手机和电脑
- 暗色模式自动跟随系统
- 数据来源：GitHub Search API
