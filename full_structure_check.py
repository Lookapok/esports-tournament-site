#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整檢查 Docker 和 Supabase 的所有表格結構和資料
"""

import psycopg2
import os

def check_docker_structure():
    """檢查 Docker PostgreSQL 的完整結構"""
    print("🐳 檢查 Docker PostgreSQL 結構")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        # 取得所有 tournaments 相關表格
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'tournaments_%'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 找到 {len(tables)} 個表格:")
        
        docker_schema = {}
        
        for table in tables:
            print(f"\n🔍 {table}:")
            
            # 檢查欄位結構
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            table_schema = []
            
            for i, (col_name, data_type, nullable, default) in enumerate(columns):
                nullable_str = "NULL" if nullable == 'YES' else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  [{i}] {col_name}: {data_type} {nullable_str}{default_str}")
                table_schema.append({
                    'name': col_name,
                    'type': data_type,
                    'nullable': nullable == 'YES',
                    'default': default
                })
            
            # 檢查資料數量和範例
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  📊 資料數量: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 2;")
                samples = cursor.fetchall()
                print(f"  🔍 前 2 筆資料:")
                for j, sample in enumerate(samples, 1):
                    print(f"    {j}. {sample}")
            
            docker_schema[table] = {
                'columns': table_schema,
                'count': count
            }
        
        cursor.close()
        conn.close()
        
        return docker_schema
        
    except Exception as e:
        print(f"❌ Docker 檢查失敗: {e}")
        return None

def check_supabase_structure():
    """檢查 Supabase 的完整結構"""
    print("\n☁️ 檢查 Supabase 結構")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="aws-1-ap-southeast-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.yqmwwyundawdictftepn",
            password="Qazwsxedc0728"
        )
        cursor = conn.cursor()
        
        # 取得所有 tournaments 相關表格
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'tournaments_%'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 找到 {len(tables)} 個表格:")
        
        supabase_schema = {}
        
        for table in tables:
            print(f"\n🔍 {table}:")
            
            # 檢查欄位結構
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            table_schema = []
            
            for i, (col_name, data_type, nullable, default) in enumerate(columns):
                nullable_str = "NULL" if nullable == 'YES' else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  [{i}] {col_name}: {data_type} {nullable_str}{default_str}")
                table_schema.append({
                    'name': col_name,
                    'type': data_type,
                    'nullable': nullable == 'YES',
                    'default': default
                })
            
            # 檢查資料數量和範例
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  📊 資料數量: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 2;")
                samples = cursor.fetchall()
                print(f"  🔍 前 2 筆資料:")
                for j, sample in enumerate(samples, 1):
                    print(f"    {j}. {sample}")
            
            supabase_schema[table] = {
                'columns': table_schema,
                'count': count
            }
        
        cursor.close()
        conn.close()
        
        return supabase_schema
        
    except Exception as e:
        print(f"❌ Supabase 檢查失敗: {e}")
        return None

def compare_schemas(docker_schema, supabase_schema):
    """比較兩個資料庫的結構差異"""
    print("\n🔄 比較結構差異")
    print("=" * 60)
    
    # 檢查表格差異
    docker_tables = set(docker_schema.keys())
    supabase_tables = set(supabase_schema.keys())
    
    print(f"📋 Docker 表格數: {len(docker_tables)}")
    print(f"📋 Supabase 表格數: {len(supabase_tables)}")
    
    missing_in_supabase = docker_tables - supabase_tables
    extra_in_supabase = supabase_tables - docker_tables
    common_tables = docker_tables & supabase_tables
    
    if missing_in_supabase:
        print(f"⚠️ Supabase 缺少表格: {missing_in_supabase}")
    if extra_in_supabase:
        print(f"ℹ️ Supabase 多出表格: {extra_in_supabase}")
    
    print(f"✅ 共同表格: {len(common_tables)}")
    
    # 檢查共同表格的結構差異
    structure_issues = []
    
    for table in common_tables:
        print(f"\n🔍 檢查 {table} 結構差異:")
        
        docker_cols = {col['name']: col for col in docker_schema[table]['columns']}
        supabase_cols = {col['name']: col for col in supabase_schema[table]['columns']}
        
        docker_col_names = set(docker_cols.keys())
        supabase_col_names = set(supabase_cols.keys())
        
        missing_cols = docker_col_names - supabase_col_names
        extra_cols = supabase_col_names - docker_col_names
        common_cols = docker_col_names & supabase_col_names
        
        if missing_cols:
            print(f"  ⚠️ Supabase 缺少欄位: {missing_cols}")
            structure_issues.append(f"{table}: 缺少欄位 {missing_cols}")
        
        if extra_cols:
            print(f"  ℹ️ Supabase 多出欄位: {extra_cols}")
        
        # 檢查共同欄位的型別差異
        type_differences = []
        for col in common_cols:
            docker_col = docker_cols[col]
            supabase_col = supabase_cols[col]
            
            if docker_col['type'] != supabase_col['type']:
                type_differences.append(f"{col}: {docker_col['type']} vs {supabase_col['type']}")
            
            if docker_col['nullable'] != supabase_col['nullable']:
                nullable_diff = f"{col} nullable: {docker_col['nullable']} vs {supabase_col['nullable']}"
                type_differences.append(nullable_diff)
        
        if type_differences:
            print(f"  ⚠️ 型別差異:")
            for diff in type_differences:
                print(f"    • {diff}")
            structure_issues.extend([f"{table}: {diff}" for diff in type_differences])
        else:
            print(f"  ✅ 欄位結構一致 ({len(common_cols)} 個欄位)")
        
        # 檢查資料數量
        docker_count = docker_schema[table]['count']
        supabase_count = supabase_schema[table]['count']
        
        if docker_count != supabase_count:
            print(f"  📊 資料數量差異: Docker({docker_count}) vs Supabase({supabase_count})")
        else:
            print(f"  ✅ 資料數量一致: {docker_count}")
    
    return structure_issues, common_tables

def main():
    """主檢查流程"""
    print("🔍 完整資料庫結構檢查")
    print("=" * 80)
    
    # 檢查 Docker
    docker_schema = check_docker_structure()
    if not docker_schema:
        print("❌ 無法檢查 Docker 結構")
        return
    
    # 檢查 Supabase
    supabase_schema = check_supabase_structure()
    if not supabase_schema:
        print("❌ 無法檢查 Supabase 結構")
        return
    
    # 比較結構
    structure_issues, common_tables = compare_schemas(docker_schema, supabase_schema)
    
    # 總結
    print("\n" + "=" * 80)
    print("📊 檢查總結")
    print("=" * 80)
    
    if structure_issues:
        print(f"⚠️ 發現 {len(structure_issues)} 個結構問題:")
        for issue in structure_issues:
            print(f"  • {issue}")
        print("\n❌ 建議先解決結構差異再進行遷移")
    else:
        print("✅ 所有表格結構完全一致！")
        print("✅ 可以安全進行資料遷移")
        
        # 顯示需要遷移的資料量
        print(f"\n📊 需要遷移的資料:")
        total_records = 0
        for table in common_tables:
            docker_count = docker_schema[table]['count']
            if docker_count > 0:
                print(f"  📋 {table}: {docker_count} 筆")
                total_records += docker_count
        
        print(f"\n📊 總計: {total_records} 筆資料需要遷移")

if __name__ == "__main__":
    main()
