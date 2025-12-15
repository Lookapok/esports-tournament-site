# bot.py (最終版：讀取本地 players.json + 模糊比對)

import discord
from discord.ext import commands
import google.generativeai as genai
import aiohttp
import json
import re
import os
import pathlib
from dotenv import load_dotenv
from thefuzz import process

# --- 1. 設定管理 (從 .env 檔案讀取) ---

dotenv_path = pathlib.Path(__file__).parent.resolve() / '.env'
load_dotenv(dotenv_path=dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DJANGO_API_URL = os.getenv("DJANGO_API_URL") 

# 檢查必要的環境變數
if not all([BOT_TOKEN, TARGET_CHANNEL_ID, GEMINI_API_KEY, DJANGO_API_URL]):
    print("❌ 錯誤：缺少必要的環境變數。請檢查 .env 是否包含 BOT_TOKEN, TARGET_CHANNEL_ID, GEMINI_API_KEY, DJANGO_API_URL。")
    exit()

try:
    TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)
except ValueError:
    print(f"❌ 錯誤：TARGET_CHANNEL_ID '{TARGET_CHANNEL_ID}' 不是一個有效的數字。")
    exit()

# 設定模糊比對的相似度門檻 (0-100)
SIMILARITY_THRESHOLD = 85

# -------------------------

# --- 2. 初始化設定 ---

genai.configure(api_key=GEMINI_API_KEY)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. AI 指令 (Prompt) ---
AI_PROMPT = """
你是一位專業且極度細心的電競數據分析師。
你的任務是從一張 Valorant 遊戲結束後的計分板截圖中，精確地提取出所有關鍵資訊。
你必須嚴格遵循以下規則，回傳一個完整的、格式正確的 JSON 物件：
1.  JSON 的最外層必須包含 "map_name", "final_score", "winning_team_name", 和 "player_stats" 這四個鍵。
2.  在 "player_stats" 陣列中，每一個物件都代表一位選手，且 **必須** 包含以下鍵值對，鍵的名稱 **必須** 完全匹配：
    - "nickname": (字串) 選手的遊戲內暱稱。
    - "acs": (數字) "平均戰鬥分數" (Average Combat Score)。
    - "kills": (數字) "擊殺" 數。
    - "deaths": (數字) "死亡" 數。
    - "assists": (數字) "助攻" 數。
    - "first_kills": (數字) "首殺" (First Kills / First Bloods) 數。
3.  計分板上的 "KDA" 欄位是一組數據，你 **必須** 將它拆分成獨立的 "kills", "deaths", 和 "assists" 三個鍵。
4.  如果圖片中缺少 "首殺" 數據，"first_kills" 的值應為 0。
5.  如果無法辨識選手暱稱，"nickname" 的值 **必須** 為 "[未知選手]"。
6.  除了這個 JSON 物件之外，絕對不要添加任何其他的說明、註解或文字。
"""

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('Bot is ready and listening...')
    print('------')

# --- 4. 主要事件處理邏輯 ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    # 解析指令 !report <match_id> "<winner_name>"
    match_command = re.match(r'!report\s+(\d+)\s+"([^"]+)"', message.content, re.IGNORECASE)

    if not match_command:
        return
        
    match_id = int(match_command.group(1))
    winner_name_from_user = match_command.group(2)
    
    if not message.attachments:
        await message.channel.send("指令錯誤：請附上一張計分板圖片。")
        return

    processing_message = await message.channel.send(
        f"✅ 收到 `Match ID: {match_id}` 的戰績回報 (指定勝者: **{winner_name_from_user}**)，"
        f"正在處理 **{len(message.attachments)}** 張圖片..."
    )

    # --- 步驟 0: 從本地檔案 players.json 讀取選手名單 ---
    try:
        # 使用 'utf-8' 編碼以支援中文
        with open('players.json', 'r', encoding='utf-8') as f:
            registered_players = json.load(f)
        
        if not registered_players:
            await processing_message.edit(content="❌ 錯誤：players.json 選手名單為空，處理中止。")
            return
            
    except FileNotFoundError:
        await processing_message.edit(content="❌ 錯誤：在 Bot 資料夾中找不到 `players.json` 選手名單檔案。")
        return
    except json.JSONDecodeError:
        await processing_message.edit(content="❌ 錯誤：`players.json` 檔案格式不正確 (JSON 語法錯誤)。")
        return

    final_success_nicknames, final_failed_nicknames = set(), set()
    
    async with aiohttp.ClientSession() as session:
        for index, attachment in enumerate(message.attachments):
            map_num = index + 1
            # 只處理圖片格式
            if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                await message.channel.send(f"⚠️ **Map {map_num}** 的檔案 `{attachment.filename}` 格式錯誤，已跳過。")
                continue

            print(f"--- 開始處理 Map {map_num} (Match ID: {match_id}) ---")
            
            try:
                # 1. 下載圖片
                async with session.get(attachment.url) as response_img:
                    if response_img.status != 200:
                        await message.channel.send(f"⚠️ **Map {map_num}** 圖片下載失敗，已跳過。")
                        continue
                    image_data = await response_img.read()

                # 2. 呼叫 Gemini AI 進行 OCR
                image_part = {"mime_type": attachment.content_type, "data": image_data}
                # 使用最新的 flash 模型
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                response_ai = await model.generate_content_async([AI_PROMPT, image_part])

                # 3. 解析 AI 回傳的 JSON
                try:
                    raw_json_text = response_ai.text.strip().replace("```json", "").replace("```", "").strip()
                    parsed_data = json.loads(raw_json_text)
                except (json.JSONDecodeError, AttributeError):
                    print(f"AI 回應格式錯誤: {response_ai.text}")
                    await message.channel.send(f"❌ **Map {map_num}** AI 回應無法解析，已跳過。")
                    continue
                
                # 4. 進行模糊比對校正
                player_stats_from_ai = parsed_data.get("player_stats", [])
                corrected_player_stats = []
                map_failed_nicknames = set()

                for player_stat in player_stats_from_ai:
                    ocr_nickname = player_stat.get("nickname", "[未知選手]")
                    
                    if ocr_nickname == "[未知選手]":
                        map_failed_nicknames.add(ocr_nickname)
                        corrected_player_stats.append(player_stat)
                        continue

                    # 使用 fuzzy matching 尋找最相似的註冊選手
                    match = process.extractOne(ocr_nickname, registered_players)
                    
                    if match and match[1] >= SIMILARITY_THRESHOLD:
                        # 分數夠高，自動校正
                        print(f"校正成功: '{ocr_nickname}' -> '{match[0]}' (相似度: {match[1]})")
                        player_stat["nickname"] = match[0] 
                    else:
                        # 分數太低，視為失敗
                        print(f"校正失敗: '{ocr_nickname}' (最接近: '{match[0]}' - {match[1]})")
                        map_failed_nicknames.add(ocr_nickname)
                    
                    corrected_player_stats.append(player_stat)

                # 5. 準備並發送資料給 Django API
                payload = {
                    "map_number": map_num,
                    "map_name": parsed_data.get("map_name"),
                    "final_score": parsed_data.get("final_score"),
                    "winning_team_name": winner_name_from_user,
                    "player_stats": corrected_player_stats
                }

                target_url = DJANGO_API_URL.format(match_id=match_id)
                headers = {'Content-Type': 'application/json'}
                
                async with session.post(target_url, headers=headers, data=json.dumps(payload)) as response_django:
                    if response_django.status in [200, 201, 207]:
                        # 處理後端回傳的結果
                        report_data = await response_django.json()
                        backend_errors = {e['nickname'] for e in report_data.get('errors', [])}
                        
                        all_nicknames_in_map = {p.get('nickname') for p in corrected_player_stats if p.get('nickname')}
                        final_map_failures = map_failed_nicknames.union(backend_errors)
                        success_nicknames_in_map = all_nicknames_in_map - final_map_failures
                        
                        final_success_nicknames.update(success_nicknames_in_map)
                        final_failed_nicknames.update(final_map_failures)
                    else:
                        error_details = await response_django.text()
                        await message.channel.send(
                            f"❌ **Map {map_num}** 資料庫寫入失敗 (錯誤碼: {response_django.status})\n"
                            f"原因: `{error_details}`"
                        )

            except Exception as e:
                import traceback
                print(f"處理 Map {map_num} 時發生例外錯誤:")
                traceback.print_exc()
                await message.channel.send(f"❌ **Map {map_num}** 發生未預期錯誤，請檢查後台日誌。")

    # --- 產生最終報告 ---
    reply_message = f"📝 **Match ID: {match_id} 總處理報告** 📝\n({len(message.attachments)} 張圖片處理完畢)\n\n"
    
    if final_success_nicknames:
        reply_message += "✅ **成功登錄選手：**\n"
        # 排序顯示，方便閱讀
        for name in sorted(list(final_success_nicknames)):
            reply_message += f"> `{name}`\n"
            
    if final_failed_nicknames:
        # 只顯示真正失敗的（排除掉已經成功的）
        unique_failed = final_failed_nicknames - final_success_nicknames
        if unique_failed:
            reply_message += "\n❌ **有問題的選手 (請檢查暱稱/隊伍)：**\n"
            for name in sorted(list(unique_failed)):
                reply_message += f"> `{name}`\n"
                
    await processing_message.edit(content=reply_message)


# --- 5. 啟動 Bot ---
if __name__ == "__main__":
    print("正在啟動 Bot...")
    bot.run(BOT_TOKEN)