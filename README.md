# 美之晨 · 線上點餐系統

[![繁體中文](https://img.shields.io/badge/README-繁體中文-2f81f7?style=flat-square)](README.md) [![English](https://img.shields.io/badge/README-English-6e7781?style=flat-square)](README.en.md)

台南永康「美之晨」早餐店的自建點餐平台。客人線上點單 → 店家後台接單 → 依實際路網自動排出最順的外送順序 → 線上付款（綠界 ECPay）自動入帳。不抽成、不靠外送平台。

## 線上網址

| 入口 | 網址 | 備註 |
|---|---|---|
| 客人點餐 | https://mzc-breakfast.pages.dev/ | Cloudflare Pages 正式站 |
| 店家後台 | https://mzc-breakfast.pages.dev/admin | 管理密碼登入（後端 Apps Script 驗證，含失敗限速） |
| 食品標示 | https://mzc-breakfast.pages.dev/sauce | 公開 |
| 客服與退換貨政策 | https://mzc-breakfast.pages.dev/policy | 公開（綠界送件審核用） |
| 舊站 | https://tewei02.github.io/mzc-breakfast/ | 僅保留轉址頁，會自動導向新站 |

> 舊站原為 GitHub Pages（免費方案不得作商業用途），已遷至 Cloudflare Pages；根目錄三個 HTML 現為轉址頁，舊連結與 QR code 不會失效。後端真實網址不再出現在任何前端檔案，也不寫進版控（見下方環境變數）。

| 菜單 | `https://mzc-breakfast.pages.dev/menu` |

## 功能

| 分類 | 內容 |
|---|---|
| 點餐 | 吐司／漢堡／蛋餅／抓餅／丹麥／總匯，口味選好再挑基底計價；飲料小杯 550ml、大杯 750ml |
| 外送 | 低消 150 元、滿 300 免運、未達加收 30 元；範圍鹽行・大橋・六甲頂；05:30–10:30 |
| 自取 | 選自取自動隱藏外送條件卡、運費歸零 |
| 商品 | 自製辣椒醬 750ml／NT$150，可店取或宅配（7-11 賣貨便／黑貓） |
| 出車排序 | 後台一鍵排出最順路徑（近→遠／遠→近／最順／手動），可一次重排全部外送單 |
| 金流 | 綠界 ECPay：信用卡、Apple Pay、Google Pay、ATM 虛擬帳號、超商代碼；付款完成自動入帳 |
| 取號 | ATM／超商取號回呼自動寫入訂單備註與「待付款（已取號）」狀態 |
| 食品標示 | `sauce.html`：辣椒醬包裝標示、營養標示與試算、瓶身貼紙、宅配包裝說明 |
| 菜單 | `menu.html`：完整價目表大圖、點擊放大、列印、`Menu` 結構化資料；首頁頁頭設入口 |
| 客服政策 | `policy.html`：客服聯絡、取消訂單、退換貨與退款（含運送異常）、金流說明、個資保護、食品業者登錄、消費爭議處理；`sauce.html` 填入登錄字號後自動同步顯示 |
| 訂單管理 | 後台可永久刪除單一訂單（二次確認）、線上修改管理密碼（不必重新部署） |
| 日期查詢 | 後台篩選列可選「今天／昨天／全部」，也能直接點日期框查任何一天（統計與空狀態跟著該日走） |
| 登入 | 後台只需輸入管理密碼；API 網址預設同網域 `/api`，一般不用改 |
| 營業狀態 | 後台一鍵設「今日公休（可附說明）」或勾選品項售完；前台顯示狀態條、售完卡片灰化並攔截下單、公休時暫停接單（仍可看菜單） |
| 訂單查詢 | 客人以「單號＋電話末三碼」查進度：已收到 → 製作中 → 可取餐／外送中 → 已完成；下方可「再來一單」把品項帶回購物車（自動跳過外送費） |
| 後台搜尋 | 姓名／電話／單號／品項即時模糊搜尋，一鍵匯出當日訂單 CSV |
| 營運統計 | 筆數、金額、客單價、外送／自取拆分、狀態分布、熱銷排行、每小時分布 |
| 新單提示 | 後台可開提示音，新單進來自動響鈴並跳提示 |
| 加到主畫面 | `manifest.webmanifest` 與 App 圖示，手機可把點餐頁存成獨立 App 樣式 |

## 系統架構

```
客人端 index.html ─┐
                    ├─ POST ─→ /api（Pages _worker.js 代理）─→ Google Apps Script (/exec) ─→ Google 試算表（訂單）
店家後台 admin.html ┘                                                    │
                                                                         └─→ 綠界 ECPay（建立訂單／付款回呼）
```

- 前端：純靜態單檔 HTML，圖片內嵌，託管於 Cloudflare Pages（https，允許商業用途）
- 代理：`public/_worker.js` 把同網域 `/api` 轉到 Apps Script，前端與原始碼都不再出現 `/exec`
- 後台保護：管理密碼登入（`admin.html` 輸入密碼，後端 Apps Script 以指令碼屬性 `ADMIN_TOKEN` 比對，含失敗次數限速；2026-11-26 已移除原本額外的 Cloudflare Access 一次性驗證碼層）
- 後端：Google Apps Script，資料存 Google 試算表，免伺服器費用
- 金流：綠界 ECPay 幕後建單 + 兩組回呼（付款結果 / 取號資訊）


## 目錄結構

| 檔案 | 說明 |
|---|---|
| `public/` | **站台原始檔，即 Cloudflare Pages 的建置輸出目錄**（改這裡才會上線） |
| `public/index.html` | 客人點餐頁（單檔，圖片內嵌） |
| `public/admin.html` | 店家後台：訂單列表、出車排序、付款狀態、綠界設定面板 |
| `public/sauce.html` | 辣椒醬食品標示頁：法定標示、營養標示試算、可列印瓶身貼紙、宅配包裝 |
| `public/menu.html` | 菜單頁：`images/menu.jpg`（2000×737 網頁用）與 `images/menu-full.jpg`（原尺寸 2467×910） |
| `public/policy.html` | 客服與退換貨政策頁：取消訂單、退款管道與時程、金流說明、個資、食品業者登錄字號、消費爭議（綠界賣家審核要件） |
| `public/_worker.js` | Pages Advanced Mode 代理層：`/api` 轉發 Apps Script，前端不再暴露 `/exec` |
| `public/manifest.webmanifest` | PWA 設定：可加到手機主畫面（含 192／512 圖示） |
| `public/images/icon-192.png`、`icon-512.png`、`apple-touch-icon.png` | App 圖示（橙底白字「晨」） |
| `public/_headers` | 安全標頭：全站 X-Frame-Options／nosniff／Referrer-Policy，後台 noindex＋no-store |
| `public/images/` | 頁面用圖片 |
| `index.html`／`admin.html`／`sauce.html`（根目錄） | 舊站轉址頁，導向新站 |
| `images/og-cover.png` | 社群分享封面 1200×630（og:image／twitter:image） |
| `上線操作說明.md` | 部署與金流操作紀錄 |
| `README.md` / `README.en.md` | 中文／英文說明，頁首可互切 |
| `scripts/check_static.py` | 靜態檔齊備、失效連結、標籤閉合、密鑰外洩檢查 |
| `.github/workflows/ci.yml` | CI：每次 push 跑檢查；舊站 Pages 部署改為手動觸發 |

## 環境變數（Cloudflare Pages）

| 變數 | 用途 | 必要性 |
|---|---|---|
| `BACKEND_URL` | Apps Script `/exec` 完整網址，供 `_worker.js` 轉發用 | 必填，未設時 `/api` 回 503 `backend_not_configured` |

設定位置：Cloudflare Dashboard → Workers & Pages → `mzc-breakfast` → Settings → Variables and Secrets → Production。**不要寫回程式碼**，本儲存庫為公開。

## 自動部署

`mzc-breakfast` 已與 GitHub `TeWei02/mzc-breakfast` 的 `main` 分支連動：`git push` 後自動建置上線（建置指令留空、輸出目錄 `public`、根目錄留空、自動部署已啟用）。

- 2026-11-27 實測：commit `9828858` 推送後 Cloudflare 自動產生部署 `880e9d53`（成功），不必再手動 `wrangler`。
- `wrangler pages deploy public --project-name mzc-breakfast --branch main` 仍可用，作為臨時手動發布的備援。


## 後端 API

所有請求 `POST` 到 Apps Script `/exec`，以 `action` 區分；管理類動作需帶 `token`。

| action | 用途 | 需 token |
|---|---|---|
| `order` | 建立新訂單 | 否 |
| `list` | 讀取訂單列表 | 是 |
| `shipped` | 標記已出車並通知 | 是 |
| `paid` | 標記已收款 | 是 |
| `route` | 計算路網距離矩陣 | 是 |
| `plan` | 依矩陣排出最順順序並寫回 | 是 |
| `ecpay` | 建立綠界付款單 | 否 |
| `ecpayCfg` | 讀取／儲存綠界設定（金鑰存 Script Properties） | 讀：否／寫：是 |
| `deleteOrder`（POST） | 永久刪除試算表上該筆訂單（整列刪除，不可復原） | 是 |
| `setToken`（POST） | 修改管理密碼，寫入指令碼屬性 `ADMIN_TOKEN` | 是（需舊密碼） |
| `soldout` | 讀取（GET）／設定（POST：`closed`、`closedNote`、`items`）今日公休與售完品項 | 讀：否／寫：是 |
| `track` | 客人查單進度：`id` ＋ `last3`（電話末三碼），回單號、品項、金額、狀態、ETA | 否 |
| `stats` | 營運統計：筆數、金額、客單、外送／自取、狀態分布、熱銷、每小時 | 是 |

> v23 起：`deleteOrder`／`delete`／`setToken` 用 GET 呼叫一律回 `ok:false`（只能用 POST），避免網址一按就假成功；不認得的 `action` 也回 `ok:false`。
> 下單 `order` 有必填檢查：姓名、電話（至少 7 位數字）、至少一項餐點名稱、金額大於 0，外送另需地址，不符會回 `ok:false` 並附人類可讀的 `msg`。

## 部署

### 前端（Cloudflare Pages）

```bash
git add .
git commit -m "更新說明"
git push origin main          # 版本留存用

# 實際發布：Pages 專案沒有接 Git，要用 wrangler 上傳 public/
CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... \
  npx wrangler pages deploy public --project-name mzc-breakfast --branch main
```

`public/` 是發布目錄，`_worker.js` 會把同網域的 `/api` 代理到環境變數 `BACKEND_URL` 指向的 Apps Script。

### 後端（Apps Script）

```bash
clasp push --force
clasp update-deployment <舊 deploymentId> -d "版本說明"   # 建新版本並更新同一部署
```

> 一定要更新「同一個 deploymentId」，`/exec` 網址才不會變（`BACKEND_URL` 不必改）。
> 目前正式部署 ID 開頭為 `AKfycbzNoO78…`（v23）。

### CI（GitHub Actions）

`.github/workflows/ci.yml` 於每次 push／PR 自動執行：

- 檢查必要靜態檔（`index.html`、`admin.html`、`sauce.html`、`README.md`、`README.en.md`、`LICENSE`）是否齊備
- 解析所有本地 `href` / `src`，連結指向不存在的檔案即失敗
- 檢查 HTML 可解析性，標籤未閉合時列出警告
- 掃描是否誤提交密鑰（綠界 HashKey／HashIV、Apps Script 部署網址、管理密碼）

另附 `deploy` job（僅手動 `workflow_dispatch` 觸發），用官方 GitHub Pages actions 發布；需先在 **Settings → Pages → Source** 設為 **GitHub Actions**。

## 金流上線（綠界）

1. 申請綠界個人賣家（需身分證、存簿封面、營業場所照 3 張、可存取的販售網址）
2. 通過後於廠商後台取得：商店代號、HashKey、HashIV
3. 後台 `admin.html` → 金流設定 → 切「正式環境」→ 貼上三碼 → 儲存
4. 下一筆訂單即走正式環境，付款完成自動寫回試算表

> 測試環境使用綠界公開測試號 `2000132`，付款不會真的入帳，可安心測流程。

## 辣椒醬食品標示

`sauce.html` 依《食品安全衛生管理法》第 22 條整理，含：

1. **法定應標事項**：品名、內容物（由多到少）、食品添加物、淨重、有效日期與保存期限、保存條件、原產地、過敏原警語、製造廠商名稱電話地址、食品業者登錄字號、使用方式
2. **營養標示**：每 100 公克與每份雙欄；附配料重量與營養試算工具（輸入配方重量與食材營養值即可算出整批與每份數值）
3. **瓶身貼紙**：約 6×8 公分，可直接列印裁切貼瓶
4. **宅配包裝**：外箱標示、氣泡布緩衝、封膜與滲漏處理、客服資訊

> 標示頁所有欄位可直接在瀏覽器點擊編輯，修改存在該裝置的 localStorage，改完按「列印／存成 PDF」即可。
> 營養數值請以送驗報告或食品營養成分資料庫計算結果為準，頁面內的試算僅供初步估算。

## 安全說明

- 綠界金鑰存於 Apps Script「指令碼屬性」，**不寫進 repo**、不出現在網址
- 此 repo 為公開，訂單個資（姓名、電話、地址）只存試算表，勿上傳
- 管理密碼以 Apps Script「指令碼屬性 `ADMIN_TOKEN`」為準，後台設定頁可直接線上修改（8 碼以上、英數混合），改完立即生效、不必重新部署
- 未設定 `ADMIN_TOKEN` 前會退回程式碼中的預設值；實際密碼不寫在文件裡，請於後台設定頁自行設定
- 匯款提醒已寫入客人端頁面，降低假冒店家改帳號的詐騙風險

## 待辦

- [x] 辣椒醬食品標示頁（`sauce.html`）與宅配包裝說明
- [x] 後台可刪除單一訂單、線上修改管理密碼
- [x] Pages 接 GitHub 自動部署（2026-11-27 完成並實測 push 觸發）
- [x] 舊全權 API Token `mzc-marvis` 作廢（2026-11-27，僅留 `mzc-marvis-20261127`）
- [x] 網站端合規頁面 `/policy`（客服、取消、退換貨與退款、金流、個資、爭議處理）已上線，首頁資訊卡與頁尾、菜單頁皆設入口（2026-11-27，commit `9fbcda9`）
- [ ] 綠界送件環境照 3 張：實拍後放入 `~/Downloads/美之晨_環境照_待上傳/`（本機與雲端目前均無店家實拍原圖，AI 合成圖不可用）
- [ ] 綠界正式商店代號申請與三碼設定（照抄版見 `輸出/美之晨_綠界個人賣家_申請資料表_20261127.md`，含網站合規自查與費率）
- [ ] 食品業者登錄字號：至 fadenbook.fda.gov.tw 線上申辦，當日可取得 16 碼字號，填入 `sauce.html` 瓶身貼紙「登錄字號」欄
- [x] 門牌統一為「臺南市永康區塩興里新行街 272 號」（與 Google 商家檔案、OSM 反查一致），全站 meta／頁尾／標示貼紙／菜單頁已同步
- [x] 營養標示：v24.2 已內建一鍵試算（配方加權）並自動套用至標示表與貼紙；送驗後以報告數值覆蓋即可
- [x] 舊版外送路線圖 `route.png`：確認 repo 內已無此檔、頁面亦未引用（僅有同名 CSS class `.route`），項目關閉
- [ ] LINE 官方帳號（建議先開免費輕用量）
- [x] 測試單（T1115001540、T1115001606C）已自試算表清除（2026-11-25，剩 14 筆）
- [x] v24 自動測試單全數清除、售完／公休狀態復原（2026-11-27，今日 0 筆）

## 授權

本專案為店家私有系統，版權所有。未經授權請勿複製、改作或商業使用。

---

*維護：柯德瑋（TeWei02）*
