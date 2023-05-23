# vulnerable-web
脆弱性有のWebサイト(本番環境での使用厳禁)

- SQL Injection(Username側の文字)

## 初期セットアップ
```bash
pip3 install -r requirements.txt
chmod a+x main.py
```

## 起動方法
```bash
./main.py
```

8080/tcp で起動します

http://127.0.0.1:8080 でアクセス出来ます
