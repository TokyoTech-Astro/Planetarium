# RaspberryPiの基本情報

pi-controller(球外のpi)とpi-starsphere(球内のpi)の2枚を使用。

pi-controllerがオーディオ、モータ、恒星、ウェブサーバを担当。\
pi-starphereが星座、一等星を担当。

ホスト名
- pi-controller.local
- pi-starsphere.local

ユーザ名: pi \
パスワード: raspberry

## wifiへの自動接続
記憶が怪しいがnmcliで設定してた気がする。軽く調べて`../memo_wifi.txt`に申し訳程度にまとめておいたのでそちらを参照。

## bluetoothスピーカーへの自動接続
`apiServerAudio/autoconnector.sh`をcrontabで定期的に実行。\
＊ちょっと動作が怪しいので改良が必用。前繋がらなかったときは一回ペアリングを解除してから再接続したら解決した。

`../README.md`に情報あり。


# 各ディレクトリの説明

## httpServer
- スマホで操作するためのウェブページのサーバ
- Next.js + Material-UI(MUI)
- pm2を使いラズパイ本体起動時に自動起動
- `http://pi-controller.local:3000`でアクセス可能
- pi-controllerで動作

## apiServerAudio
- 音声を再生するAPIを提供
- bluetoothスピーカーへの自動接続スクリプトも含まれている
- pi-controllerで動作
- `pi-controller.local:8001`で動作

## apiServerMotor
- モータを駆動するAPIを提供
- pi-controllerで動作
- `pi-controller.local:8000`で動作

## apiServerLED
- LEDのを制御するAPIを提供
- pi-controllerとpi-starsphere(球内のpi)の両方で全く同じコードが実行されている
- `pi-starsphere.local:8002`、`pi-controller.local:8002`で動作

# デプロイ方法

## 環境変数
LEDのピンアサインや番組構成を変更する場合はこれらのファイルを書き換える。
- `leds.json`
- `k2023.json`
- `httpServer/.env`

各サブディレクトリ内にこれらへのシンボリックリンクが配置されていて、プログラムではシンボリックリンクを参照している。
- `apiServerLED/leds.json`と`httpServer/src/leds.json`は`leds.json`へのシンボリックリンクである。
- `httpServer/src/k2023.json`は`k2023.json`へのシンボリックリンクである。
- `httpServer/.env`のシンボリックリンクはなくプログラムから直接参照されている。

## サーバー自動起動設定

### httpServer
pm2を使って自動起動 \
See also: `memo_pm2.txt` `https://zenn.dev/dokokade/articles/452b5376f9e260`

### apiServerLED, apiServerMotor
systemdを使ってラズパイ起動時にソフトも自動起動

### apiServerAudio
apiServerLEDやapiServerMotorと同じくsystemdを使っているが--userオプションが必用。

