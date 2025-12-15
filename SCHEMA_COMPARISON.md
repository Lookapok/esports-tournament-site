# 🔍 Docker vs Supabase 結構差異分析報告

## 📊 結構比對結果

### ✅ **一致的表格**

#### 1. `tournaments_tournament` ✅
- **欄位完全一致**

#### 2. `tournaments_player` ✅  
- **欄位完全一致**

#### 3. `tournaments_group` ✅
- **欄位完全一致**

#### 4. `tournaments_standing` ✅
- **欄位完全一致**

#### 5. `tournaments_playergamestat` ✅
- **欄位完全一致**

### ⚠️ **有差異的表格**

#### 1. `tournaments_team` ⚠️
**Docker 有的欄位：**
- `id`, `name`, `logo`

**Supabase 模型有的欄位：**
- `id`, `name`, `school`, `logo` 

**差異：**
- Supabase 多了 `school` 欄位
- **影響：** 匯入時忽略 `school` 欄位即可

#### 2. `tournaments_match` ⚠️
**Docker 欄位：**
- `id`, `round_number`, `team1_score`, `team2_score`, `match_time`, 
- `status`, `is_lower_bracket`, `team1_id`, `team2_id`, `winner_id`, 
- `tournament_id`, `map`

**Supabase 模型欄位：**
- `id`, `tournament_id`, `round_number`, `map`, `team1_id`, `team2_id`, 
- `team1_score`, `team2_score`, `winner_id`, `match_time`, `status`, 
- `is_lower_bracket`

**差異：**
- **欄位順序不同，但內容相同** ✅

#### 3. `tournaments_game` ⚠️
**Docker 欄位：**
- `id`, `map_number`, `map_name`, `team1_score`, `team2_score`, 
- `match_id`, `winner_id`

**Supabase 模型欄位：**
- `id`, `match_id`, `map_number`, `map_name`, `team1_score`, `team2_score`, 
- `winner_id`

**差異：**
- **欄位順序不同，但內容相同** ✅

## 🎯 **結論**

**好消息：** 結構基本一致！主要差異只是：

1. **`tournaments_team`** 表格 Supabase 多了 `school` 欄位（不影響匯入）
2. **欄位順序不同**（不影響匯入）

## 📝 **匯入策略**

可以直接進行資料匯入，因為：

✅ **所有關鍵欄位都存在**
✅ **資料型別相容**
✅ **外鍵關係一致**

**建議的匯入腳本調整：**

1. `tournaments_team` - 匯入時設定 `school=""` 或忽略此欄位
2. 其他表格可以直接按欄位名稱匯入

## 🚀 **下一步**

可以直接執行資料匯入，結構已經相容！
