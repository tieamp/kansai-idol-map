# 関西アイドル組数マップ

関西のアイドルグループを、ファンの情報提供で集めて一覧・ランキング化する静的サイトです。

- 部門：「グループ部門」と「ソロ部門」をタブで切り替え（集計・ランキングも部門ごと）
- 掲載条件：Xに公式アカウントがあること
- 集める情報：グループ名 / Xアカウント / YouTubeチャンネル（あれば）＋エリア・メンバー数・結成年・フォロワー数など
- 影響力：Xフォロワー数 ＋ YouTube登録者数

## 公開手順（GitHub Pages）

1. GitHubで新しいリポジトリを作り、このフォルダの中身をすべてアップロード
2. Settings → Pages → Source を `Deploy from a branch`、Branch を `main` / `(root)` にして保存
3. 数分後に `https://ユーザー名.github.io/リポジトリ名/` で公開されます
4. Settings → Issues が有効になっていることを確認（情報提供の受付に使います）
5. Issues → Labels で `add-group` と `approved` の2つのラベルを作成

## 運用の流れ

1. ファンがサイトの「グループを教える」ボタンから Issue フォームを送信
2. 管理人がXアカウントなどを確認し、問題なければ `approved` ラベルを付ける
3. 自動で `data/groups.json` に反映され、Issue が閉じられる（サイトは数分で更新）

同じXアカウントの情報が来た場合は、既存データが更新されます。

## 直接編集する場合

`data/groups.json` に次の形式で追記できます。

```json
{
  "type": "group",
  "name": "グループ名",
  "x": "example_idol",
  "youtube": "https://www.youtube.com/@example",
  "area": "大阪",
  "members": 5,
  "formedYear": 2020,
  "xFollowers": 1234,
  "ytSubscribers": 567
}
```

`type` は `"group"`（グループ）か `"solo"`（ソロ）。省略するとグループ扱いです。ソロの場合 `members` は不要です。

## 今後の拡張アイデア

- フォロワー数の定期自動更新（X API は有料のため、まずは手動／ファン提供）
- 地図表示、ジャンル（地下・ご当地など）タグ、推移グラフ
