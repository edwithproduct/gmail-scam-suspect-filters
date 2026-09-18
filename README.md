# Gmail 詐騙可疑信篩選器

把 [`mailFilters.xml`](mailFilters.xml) 匯入 Gmail。主旨命中台灣常見詐騙片語、且寄件網域不在例外清單裡時，信會略過收件匣，並標上 `scam-suspect`。

這份 XML 可直接下載匯入。匯入是快照，名單更新後要重新匯入。

## 規則怎麼判斷

Gmail 匯入後會長這樣：

```
subject:(載具歸戶異常) -{from:(gov.tw OR line.me OR shopee.tw OR ...)}
```

`-` 代表「不是」。所以：

| 主旨有關鍵字 | 來自例外網域（政府、官方平台） | 結果 |
|---|---|---|
| 有 | 是 | 留在收件匣 |
| 有 | 否 | 略過收件匣，標 `scam-suspect` |
| 無 | 不論 | 這條規則不作用 |

例外網域是官方會拿來寄信的尾綴，不是「台灣人常用的個人信箱」。`gmail.com`、`yahoo.com.tw`、`hotmail.com`、`outlook.com`、`icloud.com` 故意沒加，否則詐騙信會被放行。

## 匯入前

1. 用電腦版 Gmail。手機 App 沒有匯入篩選器。
2. 下載本 repo 的 [`mailFilters.xml`](mailFilters.xml)。
3. 若先前已匯過舊版，先到「篩選器和封鎖的地址」把舊規則刪掉。Gmail 匯入是新增，不會覆蓋，重複匯會疊兩套。

## 匯入步驟

### 1. 打開所有設定

Gmail 右上角齒輪 → 快速設定 → **查看所有設定**。

![快速設定，點查看所有設定](assets/01-quick-settings.png)

### 2. 切到篩選器分頁

設定頁上方選 **篩選器和封鎖的地址**。不要停在「一般設定」。

![設定分頁列，篩選器和封鎖的地址](assets/02-settings-tabs.png)

### 3. 點匯入篩選器

分頁底部有 **建立新篩選器** 和 **匯入篩選器**。點 **匯入篩選器**。

![建立新篩選器與匯入篩選器](assets/03-import-filters.png)

### 4. 選 XML 檔

選 `mailFilters.xml`。用文字編輯器打開會看到 `<feed>` 和 `doesNotHaveTheWord`，那是正確格式。

![選取 XML 檔案](assets/04-choose-xml.png)

選好後，頁面上會顯示檔名，再按 **開啟檔案**。

![已選取 XML，按開啟檔案](assets/05-file-selected.png)

### 5. 建立篩選器

Gmail 會列出即將建立的規則，勾選後按 **建立篩選器**。

![建立篩選器，可勾選套用到既有郵件](assets/06-create-filters.png)

**將新篩選器套用到既有的電子郵件**：勾了會連信箱裡已經存在、符合條件的信一併略過收件匣並貼標。只想攔之後進來的信，就不要勾。第一次建議先不勾，確認規則無誤再考慮補套。

匯入後標籤 `scam-suspect` 若不存在，Gmail 會自動建立。

## 這份 XML 裡有什麼

23 條規則，主旨都是較長的詐騙片語，例如：載具歸戶異常、發票中獎通知、稅務退稅通知、補繳關稅、交通違規逾期、誤設分期付款、止付驗證、金流驗證、已攔阻可疑登入。沒有用「訂單」「發票」「驗證」這種短字，誤殺會太大。

例外網域分兩塊。

**政府與學校**

- `gov.tw`
- `edu.tw`、`sinica.edu.tw`
- `gov.taipei`：臺北市政府公務信已從 `taipei.gov.tw` 改過來

**常用平台官方寄信網域**

- 帳號與通訊：LINE、Google 官方、Apple、Microsoft 官方、Facebook／Instagram
- 購物、外送、旅遊：蝦皮、PChome、momo、博客來、露天、樂天市場、foodpanda、Uber／Uber Eats、Klook、KKday、易遊網、Trip.com（含舊網域 ctrip.com）、Airbnb
- 求職：104、1111、yes123、518、Cake（`cake.me`、`cakeresume.com`）
- 生活娛樂：秀泰（`showtimes.com.tw`）、威秀（`vscinemas.com.tw`）
- 電信：中華電信、台灣大哥大、遠傳
- 超商與物流：全家、7-11／ibon、萊爾富、OK、新竹物流、黑貓、高鐵
- 支付與日常消費：街口、全聯、家樂福、好市多、中油、台電、悠遊卡
- 銀行：台銀、土銀、一銀、華南、彰銀、兆豐、富邦、國泰世華、中信、玉山、台新、永豐、合庫、LINE Bank、樂天銀行、將來銀行

完整網域清單在 XML 的 `doesNotHaveTheWord`。

## 貢獻

歡迎 fork，改名單或補詐騙主旨後開 Pull Request。

`main` 有保護規則：不能直接 push，也不能自己把 PR 合進去。維護者 review 後才會合併。

建議改 `generate.py` 裡的 `SUBJECTS` 或 `PLATFORM_DOMAINS`，跑完把更新後的 `mailFilters.xml` 一併提交。
