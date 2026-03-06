# AWS SAA-C03 Quiz App

AWS Solutions Architect Associate (SAA-C03) 練習題應用程式。

## 技術棧

| 層級 | 技術 |
|------|------|
| 語言 | Python 3.12 |
| 後端框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 資料庫 | PostgreSQL 17 |
| 資料庫遷移 | Alembic |
| 套件管理 | uv |
| Python 版本管理 | pyenv |
| Lint / Format | Ruff |
| 型別檢查 | mypy, Pyright |
| 容器化 | Docker Compose |
| CI | GitHub Actions |

## 前置需求

- [pyenv](https://github.com/pyenv/pyenv)
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose

## 快速開始

### 1. Clone 專案

```bash
git clone <repo-url>
cd aws-saa03
```

### 2. 安裝 Python

```bash
pyenv install 3.12.13   # 版本定義在 .python-version
```

### 3. 安裝依賴

```bash
cd backend
uv sync              # 安裝所有依賴（含 dev）
```

> **注意**：`uv` 會把套件裝在專案的 `.venv` 虛擬環境裡，執行 CLI 工具一律用 `uv run`。

### 4. 設定環境變數

複製範例並依需求修改：

```bash
cp .env.example .env
```

需要設定的變數請參考 `.env.example`。

### 5. 啟動 PostgreSQL

```bash
docker compose up -d
```

這會啟動：
- **PostgreSQL 17** — port `5432`
- **Adminer**（資料庫管理 UI）— port `8080`

### 6. 初始化 Alembic（僅首次）

```bash
uv run alembic init alembic
```

初始化後需要設定 `alembic/env.py`，讓它從 `.env` 讀取資料庫連線資訊。

### 7. 資料庫遷移（Alembic）

```bash
# 產生遷移檔（根據 models.py 的變更自動產生）
uv run alembic revision --autogenerate -m "描述這次變更"

# 執行遷移（升級到最新版本）
uv run alembic upgrade head

# 查看目前版本
uv run alembic current

# 回退一個版本
uv run alembic downgrade -1
```

### 8. 啟動開發伺服器

```bash
uv run uvicorn api.main:app --reload
```

API 文件：http://localhost:8000/docs

## 開發工具

所有工具都透過 `uv run` 執行：

```bash
# Lint 檢查
uv run ruff check

# 自動修復 lint 問題
uv run ruff check --fix

# 程式碼格式化
uv run ruff format

# 格式化檢查（不修改檔案）
uv run ruff format --check

# 型別檢查（mypy）
uv run mypy --ignore-missing-imports api

# 型別檢查（pyright）
uv run pyright
```

## 專案結構

```
aws-saa03/
├── .github/workflows/    # CI 設定
├── .python-version       # Python 版本（pyenv + CI 共用）
├── backend/
│   ├── alembic/          # 資料庫遷移
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/     # 遷移檔案
│   ├── alembic.ini       # Alembic 設定
│   ├── api/
│   │   ├── __init__.py
│   │   ├── db.py         # 資料庫連線與 session
│   │   ├── main.py       # FastAPI 進入點
│   │   ├── models.py     # SQLAlchemy ORM models
│   │   └── routers/      # API 路由
│   │       ├── health.py
│   │       └── questions.py
│   ├── docker-compose.yml
│   ├── pyproject.toml    # 依賴與工具設定
│   └── .env              # 環境變數（不納入版控）
└── scripts/
    └── issues.sh
```

## CI

GitHub Actions 在每次 push / PR 時自動執行：

1. **Lint** — `ruff check`
2. **Format** — `ruff format --check`
3. **Type check** — `mypy`
4. **Test** — `pytest`
