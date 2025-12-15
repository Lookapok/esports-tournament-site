#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查 Docker PostgreSQL 的完整表格結構
"""

import psycopg2

def check_docker_schema():
    """檢查 Docker 資料庫的表格結構"""
    
    docker_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'esports_dev',
        'user': 'postgres',
        'password': 'esports123'
    }
    
    try:
        conn = psycopg2.connect(**docker_config)
        cursor = conn.cursor()
        
        # 要檢查的表格
        tables = [
            'tournaments_tournament',
            'tournaments_team', 
            'tournaments_player',
            'tournaments_match',
            'tournaments_game',
            'tournaments_group',
            'tournaments_standing',
            'tournaments_playergamestat'
        ]
        
        print("🔍 Docker PostgreSQL 表格結構分析")
        print("=" * 60)
        
        for table in tables:
            print(f"\n📋 {table}:")
            print("-" * 40)
            
            # 取得欄位資訊
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                col_name, data_type, nullable, default = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  {col_name:<20} {data_type:<15} {nullable_str}{default_str}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    check_docker_schema()
