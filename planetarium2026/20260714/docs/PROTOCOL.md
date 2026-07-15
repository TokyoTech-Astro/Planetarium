# 通信仕様

## PC ⇔ 統括 (USB UART, 115200 bps, UTF-8 JSON Lines)

PCから送る主コマンド:

```json
{"cmd":"set","seq":12,"motor":{"angle":30.0,"speed":4.0},"light":{"first":true,"stars":true,"patterns":[true,false,false,false,false,false,false,false]}}
{"cmd":"config","esp_interval_ms":10000,"retry_timeout_ms":500,"max_retries":5}
{"cmd":"ping"}
{"cmd":"motor_cal","action":"jog_cw","speed":2.0,"value":0}
{"cmd":"motor_cal","action":"move_relative","speed":2.0,"value":-5.0}
{"cmd":"motor_cal","action":"set_zero","speed":0,"value":0}
{"cmd":"motor_cal","action":"set_angle","speed":0,"value":12.5}
{"cmd":"motor_cal","action":"exit","speed":0,"value":0}
```

統括からは `hello`, `status`, `event`, `pong` を返信します。`status` は各子機の通信状態、最終通信時刻、実際に反映された値を含みます。

`motor_cal` のactionは `jog_cw`, `jog_ccw`, `stop`, `move_relative`, `set_zero`, `set_angle`, `exit` です。校正コマンド受信後はモーターへの通常周期設定を一時停止し、`exit` で速度0として通常制御へ戻します。ライトへの周期送信は校正中も継続します。

## ESP-NOW

`protocol.h` のpacked固定長構造体を使用します。全パケットにmagic、version、type、sequenceを持たせます。統括は設定変更時に即送信し、通常時も設定間隔ごとに再送します。子機ACKがタイムアウトした場合は最大5回再送し、その間を不安定、終了後を途絶と判定します。

モーター校正には `MOTOR_CAL` と `MotorCalPayload` を使用し、通常のモーターACKで校正後の論理角度と速度を返信します。

固定MAC（ローカル管理アドレス）:

- 統括: `02:50:4C:41:4E:01`
- ライト: `02:50:4C:41:4E:02`
- モーター: `02:50:4C:41:4E:03`

## 現行プロトコル（Version 3）

- `AckPayload.angleDeg` は目標角度ではなく、統括・モーターマイコンが管理している実機の現在角度です。通常時は `0.0°以上360.0°未満` に正規化され、UIの「目標角度」行にある「実機現在値」へ表示されます。
- 目標角度 `999` は時計回り、`-999` は反時計回りの連続回転コマンドです。どちらも物理角度ではありません。連続回転中もACKの `angleDeg` は現在角度を返します。
- `AckPayload.uptimeMs` は各マイコンの起動後経過時間です。
- モーター校正中のUART `status.actual.motor.speed` は符号付きです。正は時計回り、負は反時計回り、0は停止を示します（ESP-NOWの構造体形式は変更しません）。
- 校正中の動作種別はUART `status.actual.motor.motion` で通知します。値は `jog_cw`（時計回り連続回転）、`jog_ccw`（反時計回り連続回転）、`relative`（相対角度移動）、`stopped`（停止）です。
- `status.actual.motor.target_angle` は位置移動の論理目標角度（0°以上360°未満）です。UIは相対角度移動中にこの値を表示します。
- `LightPayload.heartbeatTimeoutMs` はライト制御基板が通信切断と判断する時間です。統括側はESP-NOW定期送信間隔からこの値を算出して送信します。
- `LightPayload.fade` は、音声再生中にタイムラインが自然進行して設定値が変化した場合だけ `1` になります。ライト基板は恒星・一等星・星座出力を約1.2秒でフェードします。手動操作、シーク、再接続、即時送信では `0` となり即時反映します。

## 緊急停止

- PCから `{"cmd":"emergency_stop"}` を受けると、統括・モーター基板は緊急停止状態をラッチします。
- モーターの連続回転、位置移動、校正ジョグを直ちに停止し、回転速度を0にします。
- 一等星、恒星、星座1～8をすべてOFFとしてライト基板へ即時送信します。
- 緊急停止中の通常設定およびモーター校正指令は拒否されます。
- `{"cmd":"emergency_stop_release"}` を受けるまで、UARTの定期設定やタイムライン指令では解除されません。
- `status.emergency_stop` で現在のラッチ状態をUIへ通知します。
- ライト制御基板は有効な `LIGHT_SET` の最終受信から `heartbeatTimeoutMs` を超えると切断状態とし、D6の状態LEDを高速点滅します。正常時はゆっくり点滅します。
- 構造体変更によりVersion 3と旧Versionには互換性がありません。統括・モーター側とライト側を同じ版へ書き換えてください。

Wi-Fiチャネルは1に固定しています。
