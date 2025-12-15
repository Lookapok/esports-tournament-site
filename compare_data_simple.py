"""
比較 Docker 資料和線上網站資料
"""
import json
import requests
import sys

def load_docker_data():
    """載入 Docker 原始資料"""
    print("📂 載入 Docker 原始資料...")
    with open('production_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_online_data():
    """從線上網站取得資料"""
    print("🌐 從線上網站取得資料...")
    base_url = "https://winnertakesall-tw.onrender.com"
    
    try:
        # 取得錦標賽列表
        response = requests.get(f"{base_url}/api/tournaments/", timeout=10)
        if response.status_code == 200:
            tournaments = response.json()
        else:
            print(f"❌ 無法取得錦標賽資料: HTTP {response.status_code}")
            return None
        
        # 取得 Tournament 9 的詳細資料
        if tournaments:
            tournament_id = 9  # WTACS S1 的 ID
            
            # 取得隊伍資料
            teams_response = requests.get(f"{base_url}/api/tournaments/{tournament_id}/teams/", timeout=10)
            teams = teams_response.json() if teams_response.status_code == 200 else []
            
            # 取得積分榜資料
            standings_response = requests.get(f"{base_url}/api/tournaments/{tournament_id}/standings/", timeout=10)
            standings = standings_response.json() if standings_response.status_code == 200 else []
            
            # 取得比賽資料
            matches_response = requests.get(f"{base_url}/api/tournaments/{tournament_id}/matches/", timeout=10)
            matches = matches_response.json() if matches_response.status_code == 200 else []
            
            return {
                'tournaments': tournaments,
                'teams': teams,
                'standings': standings,
                'matches': matches
            }
        else:
            print("❌ 沒有找到錦標賽資料")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求失敗: {e}")
        return None
    except Exception as e:
        print(f"❌ 取得線上資料時發生錯誤: {e}")
        return None

def compare_basic_stats(docker_data, online_data):
    """比較基本統計資料"""
    print("\n" + "=" * 60)
    print("📊 Docker vs 線上網站 資料比較")
    print("=" * 60)
    
    # Docker 統計
    docker_stats = {
        'tournaments': len(docker_data.get('tournaments', [])),
        'teams': len(docker_data.get('teams', [])),
        'players': len(docker_data.get('players', [])),
        'matches': len(docker_data.get('matches', [])),
        'games': len(docker_data.get('games', [])),
        'groups': len(docker_data.get('groups', [])),
        'standings': len(docker_data.get('standings', [])),
    }
    
    # 線上統計
    online_stats = {
        'tournaments': len(online_data.get('tournaments', [])),
        'teams': len(online_data.get('teams', [])),
        'players': 'N/A',  # API 沒有提供
        'matches': len(online_data.get('matches', [])),
        'games': 'N/A',  # API 沒有提供
        'groups': 'N/A',  # API 沒有提供
        'standings': len(online_data.get('standings', [])),
    }
    
    comparisons = [
        ('tournaments', '錦標賽'),
        ('teams', '隊伍'),
        ('players', '球員'),
        ('matches', '比賽'),
        ('games', '遊戲'),
        ('groups', '分組'),
        ('standings', '排名'),
    ]
    
    print(f"{'項目':<10} {'Docker':<8} {'線上':<8} {'狀態'}")
    print("-" * 35)
    
    for key, name in comparisons:
        docker_count = docker_stats[key]
        online_count = online_stats[key]
        
        if online_count == 'N/A':
            status = "⚠️ N/A"
        elif docker_count == online_count:
            status = "✅ 一致"
        else:
            status = f"❌ 差{online_count - docker_count}" if isinstance(online_count, int) else "❌ 不同"
        
        print(f"{name:<10} {docker_count:<8} {str(online_count):<8} {status}")

def compare_detailed_data(docker_data, online_data):
    """比較詳細資料"""
    print("\n🔍 詳細資料比較:")
    
    # 比較錦標賽
    print(f"\n📋 錦標賽詳細:")
    if docker_data.get('tournaments') and online_data.get('tournaments'):
        docker_tournament = docker_data['tournaments'][0]
        online_tournament = next((t for t in online_data['tournaments'] if t.get('id') == 9), None)
        
        if online_tournament:
            print(f"  Docker: ID={docker_tournament.get('id')}, Name={docker_tournament.get('name')}")
            print(f"  線上:   ID={online_tournament.get('id')}, Name={online_tournament.get('name')}")
            print(f"  狀態:   {'✅ 一致' if docker_tournament.get('name') == online_tournament.get('name') else '❌ 不同'}")
        else:
            print("  ❌ 線上沒有 Tournament 9")
    
    # 比較隊伍
    print(f"\n🏆 隊伍比較:")
    if docker_data.get('teams') and online_data.get('teams'):
        docker_teams = {team['name'] for team in docker_data['teams']}
        online_teams = {team['name'] for team in online_data['teams']} if online_data['teams'] else set()
        
        print(f"  Docker 隊伍數: {len(docker_teams)}")
        print(f"  線上隊伍數:   {len(online_teams)}")
        
        missing_online = docker_teams - online_teams
        extra_online = online_teams - docker_teams
        
        if not missing_online and not extra_online:
            print("  ✅ 隊伍完全一致")
        else:
            if missing_online:
                print(f"  ❌ 線上缺少: {len(missing_online)} 隊")
                for team in list(missing_online)[:3]:
                    print(f"    - {team}")
                if len(missing_online) > 3:
                    print(f"    ... 還有 {len(missing_online)-3} 隊")
            
            if extra_online:
                print(f"  ⚠️ 線上多出: {len(extra_online)} 隊")
                for team in list(extra_online)[:3]:
                    print(f"    + {team}")
    
    # 比較積分榜
    print(f"\n🎯 積分榜比較:")
    if docker_data.get('standings') and online_data.get('standings'):
        print(f"  Docker 積分記錄: {len(docker_data['standings'])}")
        print(f"  線上積分記錄:   {len(online_data['standings'])}")
        
        if len(docker_data['standings']) == len(online_data['standings']):
            print("  ✅ 積分記錄數量一致")
        else:
            print(f"  ❌ 積分記錄差異: {len(online_data['standings']) - len(docker_data['standings'])}")

def main():
    print("🔄 開始比較 Docker 和線上網站資料...")
    print("=" * 60)
    
    try:
        # 載入 Docker 資料
        docker_data = load_docker_data()
        print("✅ Docker 資料載入成功")
        
        # 取得線上資料
        online_data = get_online_data()
        if not online_data:
            print("❌ 無法取得線上資料，停止比較")
            return
        print("✅ 線上資料取得成功")
        
        # 進行比較
        compare_basic_stats(docker_data, online_data)
        compare_detailed_data(docker_data, online_data)
        
        print("\n" + "=" * 60)
        print("✅ 資料比較完成")
        
    except FileNotFoundError:
        print("❌ 找不到 production_data.json 檔案")
    except Exception as e:
        print(f"❌ 比較過程中發生錯誤: {e}")

if __name__ == '__main__':
    main()
