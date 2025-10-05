# Docker 資料庫轉移指南

## 🐳 Docker PostgreSQL 資料庫轉移

### 方法 1：資料庫備份與還原（推薦）

#### 在原電腦上執行：

```bash
# 1. 備份資料庫
docker exec postgres-esports pg_dump -U postgres esports_dev > esports_backup.sql

# 2. 檢查備份檔案
dir esports_backup.sql

# 3. 複製備份檔案到專案目錄（如果需要）
# 備份檔案已在專案根目錄
```

#### 在新電腦上執行：

```bash
# 1. 啟動 PostgreSQL Docker 容器
docker run -d \
  --name postgres-esports \
  -e POSTGRES_PASSWORD=your-password \
  -e POSTGRES_DB=esports_dev \
  -p 5432:5432 \
  postgres:16

# Windows PowerShell 版本：
docker run -d --name postgres-esports -e POSTGRES_PASSWORD=your-password -e POSTGRES_DB=esports_dev -p 5432:5432 postgres:16

# 2. 等待容器啟動（約10-30秒）
docker ps

# 3. 還原資料庫
docker exec -i postgres-esports psql -U postgres esports_dev < esports_backup.sql

# 4. 驗證資料是否正確匯入
docker exec postgres-esports psql -U postgres esports_dev -c "\dt"
```

### 方法 2：Docker Volume 備份（進階）

#### 在原電腦上：

```bash
# 1. 找到 PostgreSQL 容器的 Volume
docker inspect postgres-esports | grep -i volume

# 2. 停止容器
docker stop postgres-esports

# 3. 建立 Volume 備份
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_volume_backup.tar.gz -C /data .

# 4. 重新啟動容器
docker start postgres-esports
```

#### 在新電腦上：

```bash
# 1. 建立新的 Volume
docker volume create postgres_data

# 2. 還原 Volume 數據
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_volume_backup.tar.gz -C /data

# 3. 啟動容器使用現有 Volume
docker run -d \
  --name postgres-esports \
  -e POSTGRES_PASSWORD=your-password \
  -e POSTGRES_DB=esports_dev \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16
```

### 方法 3：Docker Compose（最簡單）

建立 `docker-compose.yml` 檔案：

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    container_name: postgres-esports
    environment:
      POSTGRES_PASSWORD: your-password
      POSTGRES_DB: esports_dev
      POSTGRES_USER: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./esports_backup.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 使用 Docker Compose：

```bash
# 在新電腦上啟動
docker-compose up -d

# 檢查狀態
docker-compose ps

# 停止服務
docker-compose down
```

## 🔧 完整轉移流程

### 在原電腦上：

1. **備份資料庫**
   ```bash
   docker exec postgres-esports pg_dump -U postgres esports_dev > esports_backup.sql
   ```

2. **提交到 Git**
   ```bash
   git add esports_backup.sql
   git commit -m "新增資料庫備份檔案"
   git push origin master
   ```

### 在新電腦上：

1. **複製專案**
   ```bash
   git clone https://github.com/Lookapok/esports-tournament-site.git
   cd esports-tournament-site/esports_project
   ```

2. **啟動 Docker PostgreSQL**
   ```bash
   docker run -d --name postgres-esports -e POSTGRES_PASSWORD=your-password -e POSTGRES_DB=esports_dev -p 5432:5432 postgres:16
   ```

3. **還原資料庫**
   ```bash
   docker exec -i postgres-esports psql -U postgres esports_dev < esports_backup.sql
   ```

4. **設定環境變數**
   ```bash
   copy .env.example .env
   # 編輯 .env 檔案設定資料庫連線
   ```

5. **安裝 Python 套件並啟動**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py runserver
   ```

## ⚠️ 注意事項

1. **密碼一致性**：確保新電腦上的資料庫密碼與 `.env` 檔案中的設定一致

2. **端口衝突**：確認 5432 端口沒有被其他服務占用

3. **資料庫名稱**：確認 `esports_dev` 資料庫名稱正確

4. **權限設定**：確保 Docker 有足夠權限建立容器和 Volume

## 🚀 驗證步驟

```bash
# 檢查容器狀態
docker ps

# 檢查資料庫連線
docker exec postgres-esports psql -U postgres esports_dev -c "SELECT COUNT(*) FROM tournaments_tournament;"

# 測試 Django 連線
python manage.py dbshell
```
