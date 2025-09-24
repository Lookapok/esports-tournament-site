# WTACS 賽事自動化數據管理平台

## 專案簡介

本專案是一個專為電競賽事（特別是 Valorant）設計的全方位管理平台。其核心亮點是利用 Discord Bot 結合 Google Gemini AI 視覺辨識技術，實現了賽後戰績的自動化登錄，大幅簡化了賽事管理的人力成本與時間。

管理員可以透過網站後台建立賽事、管理隊伍與選手，而參賽隊伍僅需在指定的 Discord 頻道中，透過一個簡單的指令附上計分板截圖，即可由 AI 自動完成數據的讀取與登錄，並即時反映在賽事網站的數據統計頁面上。

---

## 核心功能

* **網站前端**
    * 公開的賽事列表與詳細資訊頁面。
    * 即時更新的隊伍、選手數據統計與排行榜。
    * 清晰的賽程樹狀圖與比賽結果。

* **網站後端 (Django Admin)**
    * **賽事管理**：輕鬆建立單敗淘汰、雙敗淘汰、循環賽等多種賽制的賽事。
    * **隊伍與選手管理**：建立隊伍、新增隊員，並管理選手的詳細資料（如遊戲內暱稱）。
    * **比賽管理**：自動或手動安排賽程，並可手動修改比賽結果。
    * **數據校驗**：所有透過 API 寫入的數據，都會與後台的選手名單進行校驗，確保數據的準確性。

* **自動化戰績回報系統 (Discord Bot)**
    * **AI 視覺辨識**：採用 Google Gemini (`gemini-1.5-flash-latest`) 模型，能精準地從遊戲計分板截圖中提取每位選手的 KDA、ACS 等關鍵數據。
    * **智慧指令互動**：使用者可透過 `!report <比賽ID>` 指令，精準地回報特定場次的戰績。
    * **即時回饋系統**：Bot 會在 Discord 頻道中即時回報處理進度，並在完成後提供一份詳細的成功/失敗報告，引導使用者修正資料庫中不匹配的選手暱稱。
    * **數據守門員**：API 具備驗證機制，只會將屬於該場比賽、且暱稱完全匹配的選手數據寫入資料庫，有效防止誤植。

---

## 技術架構

本專案採用三位一體的架構，各元件職責分明：

1.  **網站後端 (The Foundation)**
    * **框架**: Django
    * **API**: Django REST Framework
    * **職責**: 提供穩定的資料庫模型、管理後台，以及一個安全的 API 接口，用於接收格式化後的比賽數據。

2.  **自動化腳本 (The Messenger & The Brains)**
    * **語言**: Python
    * **核心函式庫**:
        * `py-cord`: 用於建立 Discord Bot，監聽頻道指令與訊息。
        * `google-generativeai`: 用於與 Google Gemini API 互動，發送圖片並接收分析結果。
        * `requests`: 用於從 Discord 下載圖片，並將最終數據發送至 Django API。
    * **職責**: 作為整個自動化流程的總指揮，串連使用者、AI 與網站後端。

3.  **資料庫**
    * **類型**: SQLite (開發中) / PostgreSQL (建議部署時使用)
    * **職責**: 持久化儲存所有賽事、隊伍、選手及比賽數據。

---

## 環境設定與安裝指南

### **1. 後端 (Django 網站)**

1.  複製專案庫：`git clone <您的專案庫網址>`
2.  進入專案目錄：`cd esports_project`
3.  建立並啟用 Python 虛擬環境：
    ```bash
    python -m venv venv
    source venv/bin/activate  # Mac/Linux
    venv\Scripts\activate  # Windows
    ```
4.  安裝依賴套件：`pip install -r requirements.txt`
5.  進行資料庫遷移：
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
6.  建立後台管理員帳號：`python manage.py createsuperuser`
7.  啟動開發伺服器：`python manage.py runserver`
    * 網站後台位於 `http://localhost:8000/admin/`

### **2. 自動化腳本 (Discord Bot)**

1.  確認已安裝 Python。
2.  安裝必要的函式庫：
    ```bash
    pip install py-cord google-generativeai requests
    ```
3.  設定環境變數或修改 `bot.py` 檔案頂部的設定：
    * `BOT_TOKEN`: 您在 Discord 開發者後台取得的 Bot Token。
    * `TARGET_CHANNEL_ID`: 要監聽的 Discord 頻道 ID。
    * `GEMINI_API_KEY`: 您的 Google AI Studio API Key。
    * `DJANGO_API_URL`: 您的 Django API 網址 (開發時通常是 `http://localhost:8000/api/matches/{match_id}/stats/`)。
4.  啟動 Bot：`python bot.py`

---

## 使用教學

1.  **管理員**：
    * 登入 Django Admin 後台。
    * 建立賽事、隊伍，並將選手新增至對應的隊伍中。**請確保選手的「暱稱」欄位與他們在遊戲中的顯示名稱完全一致**。
    * 安排賽程，並將比賽的 **ID** 告知參賽隊伍。

2.  **參賽隊伍**：
    * 在比賽結束後，擷取計分板畫面。
    * 在指定的 Discord 頻道中，發送一則訊息，格式如下：
        ```
        !report <比賽ID>
        ```
        **並同時附上計分板截圖**。
    * Bot 會自動處理後續流程，並在頻道中回報處理結果。如果出現「找不到選手」的訊息，請聯繫管理員核對暱稱。

---

## 未來展望

* [ ] **部署至雲端**: 將 Django 網站與 Discord Bot 部署到雲端伺服器，實現 24/7 穩定運行。
* [ ] **升級斜線指令**: 將 `!report` 文字指令升級為更現代、體驗更好的 `/report` 斜線指令。
* [ ] **多張圖片處理**: 支援一次處理多張計分板（例如 Bo3 的三張截圖）。
* [ ] **數據視覺化**: 在網站前端引入圖表庫 (如 Chart.js)，將選手數據以更豐富的圖表形式呈現。
* [ ] **自動賽程推進**: 當一輪比賽全部回報完畢後，系統自動將勝者推進到下一輪。