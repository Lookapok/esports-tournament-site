# 1. 使用官方的 Python 3.11 slim 版本的映像檔作為基礎
FROM python:3.11-slim

# 2. 設定環境變數，優化 Python 在 Docker 中的運行
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 在容器內建立一個工作目錄 /app
WORKDIR /app

# 4. 先複製 requirements.txt 並安裝所有依賴套件
#    這樣做可以利用 Docker 的快取，如果只有程式碼變動，就不用重裝套件，建置會更快
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. 將你本地的所有程式碼複製到容器的 /app 目錄中
COPY . /app/

# 6. 設定 Gunicorn 服務要監聽的 Port
EXPOSE 8000

# 7. 容器啟動時要執行的最終指令
#    使用 gunicorn 來啟動你的 Django 專案
#    !!! 注意：請將下面的 "myproject.wsgi" 換成你自己專案的名稱 !!!
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]