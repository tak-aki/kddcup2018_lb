# kddcup2018_portal
custom leaderboard system for kddcup2018

1. django入れる
2. git pullする
3. /competition_data/input/にコンペサイトからダウンロードしたcsvファイルを突っ込む
4. /competition_data/data/src/のなかのpythonを以下の順番で実行して
    1. modify_original_files.py 元ファイルを色々整形して保存してくれる
    2. get_and_save_aq.py apiでデータ取ってきて保存してくれる
    3. make_labels.py 日毎のlabel作ってくれる
5. プロジェクトのルートディレクトリ（manage.pyがあるところ）で以下を実行する（DBが出来る）
```bash

python manage.py makemigrations
python manage.py migrate
```
6. 以下でサーバーを起動する
```bash

python manage.py runserver
```
7. http://localhost:8000/ にアクセスする
