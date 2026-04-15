# Wealth Holdings Agent

## 项目目标
本项目是一个 FastAPI 网页应用，用于规划研究工作流程、运行工具代理（Tavily、arXiv、Wikipedia），并将任务状态/结果存储在本地 SQLite（默认）中。

## 环境配置

本项目使用 `uv` 作为包管理器和虚拟环境管理工具。

### 1. 安装 uv

如果尚未安装 `uv`，请先[安装 uv](https://github.com/astral-sh/uv)。

### 2. 安装依赖（最简方式）

在项目根目录执行：

```bash
uv sync
```

### 3. 环境变量配置
复制 `.env.example` 文件为 `.env`，并填入你的 DeepSeek API Key：
```bash
cp .env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY
```

### 4. 启动本地开发服务（不装 Docker、不装 Postgres）

```bash
uv run uvicorn main:app --reload --port 8000
```

访问：http://127.0.0.1:8000/

默认会在项目目录生成 `research.db`（SQLite），不需要安装 Postgres。若要清空任务数据，删除该文件即可。

## 目录结构
- `main.py`: 项目入口文件
- `pyproject.toml`: 项目配置文件及依赖管理
 - `src/`: 代理与工具实现
 - `templates/`: 页面模板
 - `static/`: 静态资源
