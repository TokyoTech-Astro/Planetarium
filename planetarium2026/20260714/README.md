# プラネ統合制御システム 20260714

統括・モーター制御とライト制御の両方にXIAO ESP32C3を使用します。

- `firmware/coordinator`: PCとのUART、モーター直接制御、ライト基板とのESP-NOW通信
- `firmware/light_controller`: 一等星、恒星、星座1～8の出力と状態返信
- `pc_ui`: Windows操作UIとEXE
- `docs`: 配線、設定、通信仕様

従来の独立したモーター制御マイコンは廃止し、統括マイコンへ統合しました。統括・モーター基板とライト基板の2台構成です。

ESP32C3はシングルコアのため、USB CDC・ESP-NOW・JSON処理はFreeRTOS通信タスクで動作します。モーターのCLOCK生成はハードウェアタイマー割り込みへ分離しているため、通信処理中もステップパルス生成を継続します。

## ビルド

各有効プロジェクトのフォルダーで次を実行します。

```powershell
pio run
```

書き込み前に、`firmware/coordinator/platformio.ini` のモーター1回転ステップ数、マイクロステップ数、回転方向を実機に合わせてください。
