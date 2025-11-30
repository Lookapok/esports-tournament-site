"""
比較 Docker 原始資料和已知的 Supabase 雲端資料
"""
import json

def main():
    print("🔄 比較 Docker 原始資料 vs Supabase 雲端資料")
    print("=" * 70)
    
    # 載入 Docker 原始資料
    try:
        with open('production_data.json', 'r', encoding='utf-8') as f:
            docker_data = json.load(f)
        print("✅ Docker 資料載入成功")
    except Exception as e:
        print(f"❌ 載入 Docker 資料失敗: {e}")
        return
    
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
    
    # 已知的 Supabase 線上資料統計（根據之前的操作記錄）
    supabase_stats = {
        'tournaments': 1,      # WTACS S1
        'teams': 34,           # 34 支隊伍
        'players': 231,        # 231 名球員
        'matches': 144,        # 144 場比賽
        'games': 171,          # 171 局遊戲
        'groups': 4,           # A、B、C、D 四組
        'standings': 34,       # 34 個積分記錄
    }
    
    print("\n📊 資料統計比較:")
    print(f"{'項目':<12} {'Docker':<8} {'Supabase':<10} {'狀態'}")
    print("-" * 45)
    
    comparisons = [
        ('tournaments', '錦標賽'),
        ('teams', '隊伍'),
        ('players', '球員'),
        ('matches', '比賽'),
        ('games', '遊戲'),
        ('groups', '分組'),
        ('standings', '排名'),
    ]
    
    all_match = True
    
    for key, name in comparisons:
        docker_count = docker_stats[key]
        supabase_count = supabase_stats[key]
        
        if docker_count == supabase_count:
            status = "✅ 一致"
        else:
            status = f"❌ 差{supabase_count - docker_count}"
            all_match = False
        
        print(f"{name:<12} {docker_count:<8} {supabase_count:<10} {status}")
    
    print("\n" + "=" * 70)
    
    if all_match:
        print("🎉 恭喜！Docker 資料與 Supabase 雲端資料完全一致！")
    else:
        print("⚠️ 發現資料不一致，需要進一步檢查")
    
    # 詳細分析
    print("\n🔍 詳細分析:")
    
    # 檢查錦標賽
    if docker_data.get('tournaments'):
        tournament = docker_data['tournaments'][0]
        print(f"\n📋 錦標賽資訊:")
        print(f"  ID: {tournament.get('id')}")
        print(f"  名稱: {tournament.get('name')}")
        print(f"  遊戲: {tournament.get('game', 'N/A')}")
        print(f"  狀態: {tournament.get('status', 'N/A')}")
    
    # 檢查分組
    if docker_data.get('groups'):
        print(f"\n🎯 分組資訊:")
        for group in docker_data['groups']:
            print(f"  {group.get('name')} (ID: {group.get('id')})")
    
    # 檢查隊伍樣本
    if docker_data.get('teams'):
        print(f"\n🏆 隊伍樣本 (前5名):")
        for i, team in enumerate(docker_data['teams'][:5], 1):
            print(f"  {i}. {team.get('name')} (ID: {team.get('id')})")
    
    # 檢查球員樣本
    if docker_data.get('players'):
        print(f"\n👥 球員樣本 (前5名):")
        for i, player in enumerate(docker_data['players'][:5], 1):
            print(f"  {i}. {player.get('nickname')} (隊伍ID: {player.get('team_id')})")
    
    # 檢查積分榜樣本
    if docker_data.get('standings'):
        print(f"\n📈 積分榜樣本 (前5名):")
        for i, standing in enumerate(docker_data['standings'][:5], 1):
            # 找對應的隊伍名稱
            team_name = "Unknown"
            if docker_data.get('teams'):
                team = next((t for t in docker_data['teams'] if t.get('id') == standing.get('team_id')), None)
                if team:
                    team_name = team.get('name', 'Unknown')
            
            print(f"  {i}. {team_name} - {standing.get('wins', 0)}勝 {standing.get('losses', 0)}敗 ({standing.get('points', 0)}分)")
    
    print("\n" + "=" * 70)
    print("ℹ️ 注意：此比較基於已知的線上資料統計")
    print("📝 如需即時比較，請設定 DATABASE_URL 環境變數連接 Supabase")

if __name__ == '__main__':
    main()
