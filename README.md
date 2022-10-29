# IJCAI
[第86回人工知能セミナー (2022.10.29)「AIトレンド・トップカンファレンス報告会（IJCAI2022）：世界最先端のAI研究開発動向が1日でわかる！」](https://www.ai-gakkai.or.jp/event/ai-seminar/no86_jsai_seminar/)での発表で資料作成に使用しました。

## スクレイピング方法

* [category]のセッション
```python session.py [category]```
* [category]をkeywordに含むProceedingsの論文。
```python keyword.py [category]```
* 対応カテゴリ
nlp, xai, plannning

## csvファイルについて

csv/[category]/[year]_session.csv: Proceedingsで[category]のセッションだけ。  
csv/[category]/[year].csv: Proceedingsの論文でKeywordに[category]を含むもの。

分析結果は、note.ipnybにあります。
