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

@bot.command(name='player', aliases=['玩家', 'p'])
async def search_player(ctx, *, query: str = None):
    """
    查詢玩家資訊
    用法: !player [玩家名稱]
    """
    if not query:
        await ctx.send("🔍 請提供玩家名稱！\n用法: `!player 玩家名稱`")
        return
    
    # 如果快取過期，重新載入玩家列表
    if not wtacs_bot.players_cache:
        await ctx.send("⏳ 正在載入玩家資料...")
        await wtacs_bot.get_players_list()
    
    # 模糊匹配玩家
    matches = wtacs_bot.fuzzy_match_player(query)
    
    if not matches:
        await ctx.send(f"❌ 找不到玩家 '{query}'")
        return
    
    if len(matches) == 1:
        # 精確匹配，直接顯示資料
        player_name = matches[0][0]
        embed = discord.Embed(
            title=f"🏆 玩家資訊: {player_name}",
            description=f"WTACS S1 賽事數據",
            color=0x00ff00
        )
        
        # 這裡可以新增更多玩家統計資料
        embed.add_field(name="🔗 詳細資訊", 
                       value=f"[查看完整統計](https://winnertakesall-tw.onrender.com/players/)", 
                       inline=False)
        
        embed.set_footer(text="WTACS 電競賽事系統")
        await ctx.send(embed=embed)
    
    else:
        # 多個匹配結果，讓用戶選擇
        embed = discord.Embed(
            title=f"🔍 找到多個相似的玩家:",
            description=f"搜尋: '{query}'",
            color=0xffaa00
        )
        
        match_text = ""
        for i, (name, score) in enumerate(matches[:5], 1):
            match_text += f"{i}. **{name}** (相似度: {score}%)\n"
        
        embed.add_field(name="請選擇:", value=match_text, inline=False)
        embed.set_footer(text="輸入 !player [完整名稱] 查看詳細資訊")
        
        await ctx.send(embed=embed)

@bot.command(name='ranking', aliases=['排名', 'r'])
async def show_ranking(ctx):
    """
    顯示錦標賽排名
    """
    embed = discord.Embed(
        title="🏆 WTACS S1 錦標賽排名",
        description="各小組排名情況",
        color=0x0099ff,
        url="https://winnertakesall-tw.onrender.com/"
    )
    
    embed.add_field(
        name="📊 查看完整排名", 
        value="[點此查看網站完整排名](https://winnertakesall-tw.onrender.com/)",
        inline=False
    )
    
    embed.set_footer(text="WTACS 電競賽事系統")
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['幫助', 'h'])
async def show_help(ctx):
    """
    顯示幫助資訊
    """
    embed = discord.Embed(
        title="🤖 WTACS Bot 指令清單",
        description="電競賽事查詢機器人",
        color=0x9932cc
    )
    
    embed.add_field(
        name="🔍 !player [名稱]", 
        value="查詢玩家資訊和統計\n別名: !玩家, !p",
        inline=False
    )
    
    embed.add_field(
        name="🏆 !ranking", 
        value="顯示錦標賽排名\n別名: !排名, !r",
        inline=False
    )
    
    embed.add_field(
        name="🌐 網站連結", 
        value="[WTACS 官網](https://winnertakesall-tw.onrender.com/)",
        inline=False
    )
    
    embed.set_footer(text="WTACS 電競賽事系統 | Winner Takes All")
    await ctx.send(embed=embed)

@bot.command(name='stats', aliases=['統計'])
async def show_stats(ctx):
    """
    顯示機器人統計資訊
    """
    embed = discord.Embed(
        title="📊 機器人狀態",
        color=0x00ff00
    )
    
    embed.add_field(name="🏓 延遲", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="👥 玩家資料", value=f"{len(wtacs_bot.players_cache)} 位", inline=True)
    embed.add_field(name="🌐 API 狀態", value="正常", inline=True)
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """錯誤處理"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ 指令不存在！輸入 `!help` 查看可用指令")
    else:
        logger.error(f"指令錯誤: {error}")
        await ctx.send("❌ 發生錯誤，請稍後再試")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ 請設定 BOT_TOKEN 環境變數")
        exit(1)
    
    print("🚀 啟動 WTACS Discord Bot...")
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        logger.error(f"Bot 啟動失敗: {e}")
