---
description: ast-grepでASTベースのコード検索を行う
---

# ast-grep ワークフロー

ast-grepはTree-sitterを使用したASTベースのコード検索・置換ツールです。

## 基本コマンド

// turbo-all

### パターン検索
```bash
ast-grep --pattern '<pattern>' --lang <language> <path>
```

## よく使うパターン例

### Python
```bash
# クラス定義を検索
ast-grep --pattern "class $NAME" --lang python src/

# 関数定義を検索
ast-grep --pattern "def $FUNC($$$)" --lang python src/

# デコレータ付き関数
ast-grep --pattern "@$DECORATOR
def $NAME($$$)" --lang python src/

# import文を検索
ast-grep --pattern "from $MODULE import $NAME" --lang python src/

# try-except ブロック
ast-grep --pattern "try:
    $$$
except $E:
    $$$" --lang python src/
```

## パターン変数

| 変数 | 意味 |
|------|------|
| `$NAME` | 単一ノード（識別子など） |
| `$$$` | 0個以上のノード（引数リスト等） |
| `$$` | 1個以上のノード |

## JSON出力（パース可能）
```bash
ast-grep --pattern "class $NAME" --lang python src/ --json
```

## 置換（--rewrite）
```bash
ast-grep --pattern "print($MSG)" --rewrite "logger.info($MSG)" --lang python src/
```