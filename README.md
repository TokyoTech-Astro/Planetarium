# Bluetoothオーディオの使い方

## スピーカーとの接続方法

bluetoothctlを使う

[コマンド一覧](https://qiita.com/noraworld/items/55c0cb1eb52cf8dccc12)

```
$ bluetoothctl
```

デバイスの電源オン

```
# power on
# agent on
```

スキャン

```
# scan on
# scan off
```

ペアリング（スキャンで得たアドレスを指定する）

```
# pair 30:21:B0:70:83:33
# trust
```

接続

```
# connect 30:21:B0:70:83:33
```

## 音声の確認

```
aplay /usr/share/sounds/alsa/*
```

```
yt-dlp "https://www.youtube.com/watch?v=j7CDb610Bg0" -f bestaudio -o - | mplayer - -novideo
```
