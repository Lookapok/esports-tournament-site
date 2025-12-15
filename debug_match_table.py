#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查 Match 表結構問題
"""

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432", 
        database="esports_dev",
        user="postgres",
        password="esports123"
    )
    cursor = conn.cursor()
    
    print("🔍 Game 表結構:")
    cursor.execute("""
        SELECT column_name, data_type, ordinal_position
        FROM information_schema.columns 
        WHERE table_name = 'tournaments_game' 
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"  [{col[2]-1}] {col[0]}: {col[1]}")
    
    print("\n📋 Game 範例資料:")
    cursor.execute("SELECT * FROM tournaments_game LIMIT 3;")
    games = cursor.fetchall()
    
    if games:
        for i, game in enumerate(games):
            print(f"  Game {i+1}: {game[:5]}... (共 {len(game)} 欄位)")
    else:
        print("  沒有資料")
    
    # 檢查第一筆完整資料
    print("\n🔍 第一筆完整資料:")
    cursor.execute("SELECT * FROM tournaments_game LIMIT 1;")
    first_game = cursor.fetchone()
    if first_game:
        for i, value in enumerate(first_game):
            col_name = columns[i][0] if i < len(columns) else f"col_{i}"
            print(f"  [{i}] {col_name}: {value} (type: {type(value).__name__})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 錯誤: {e}")
