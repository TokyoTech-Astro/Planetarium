from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'pdf'/'プラネタリウム統合制御_システム仕様書_v20261009-2.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('JP',r'C:\Windows\Fonts\msgothic.ttc',subfontIndex=0))
c=canvas.Canvas(str(OUT),pagesize=(595.28,841.89))
c.setTitle('プラネタリウム統合制御 システム仕様書 v20261009-2')
c.setAuthor('Planetarium project')
page=0;y=0
def wrap(text,size,width):
 lines=[]
 for paragraph in str(text).split('\n'):
  line=''
  for ch in paragraph:
   if line and pdfmetrics.stringWidth(line+ch,'JP',size)>width:
    lines.append(line);line=ch
   else:line+=ch
  lines.append(line)
 return lines
def start(title):
 global page,y
 if page:c.showPage()
 page+=1
 c.setFillColor(HexColor('#14273e'));c.rect(0,758,596,84,fill=1,stroke=0)
 c.setFillColor(white);c.setFont('JP',19);c.drawString(42,789,title)
 c.setFont('JP',9);c.drawString(42,771,'システム仕様書 | v20261009-2 | 2026-10-09')
 c.setFillColor(HexColor('#627185'));c.setFont('JP',8);c.drawString(42,28,'実装参照版 / 基板への書き込み状態は別途確認');c.drawRightString(552,28,str(page))
 y=731
def heading(text):
 global y
 y-=10;c.setFillColor(HexColor('#195b86'));c.setFont('JP',12);c.drawString(42,y,text);y-=22
def para(text,size=10):
 global y
 c.setFillColor(HexColor('#263345'));c.setFont('JP',size)
 for line in wrap(text,size,510):
  c.drawString(42,y,line);y-=size*1.65
 y-=7
def table(headers,rows,widths):
 global y
 for index,row in enumerate([headers]+rows):
  cells=[wrap(v,9,w-14) for v,w in zip(row,widths)]
  height=max(len(a) for a in cells)*14+14
  x=42
  for lines,w in zip(cells,widths):
   c.setFillColor(HexColor('#e6eef5' if index==0 else '#f5f7fa'));c.rect(x,y-height,w,height,fill=1,stroke=0)
   c.setFillColor(HexColor('#263345'));c.setFont('JP',9)
   for j,line in enumerate(lines):c.drawString(x+7,y-14-j*14,line)
   x+=w
  y-=height+2
 y-=10
def box(x,yy,w,h,title,detail):
 c.setFillColor(HexColor('#edf3f8'));c.setStrokeColor(HexColor('#286185'));c.roundRect(x,yy,w,h,7,fill=1,stroke=1)
 c.setFillColor(HexColor('#14273e'));c.setFont('JP',11);c.drawCentredString(x+w/2,yy+h-22,title);c.setFont('JP',9)
 for i,line in enumerate(detail):c.drawCentredString(x+w/2,yy+h-40-i*14,line)
def arrow(x1,y1,x2,y2,label):
 c.setStrokeColor(HexColor('#286185'));c.line(x1,y1,x2,y2);c.line(x2,y2,x2-5,y2+4);c.line(x2,y2,x2-5,y2-4);c.setFillColor(HexColor('#286185'));c.setFont('JP',8);c.drawCentredString((x1+x2)/2,y1+8,label)

start('1. システム概要・適用範囲')
para('PCの音声再生時間を基準に、ステッピングモーターと恒星・一等星・星座ライトを同期制御する。対象は20261009-2フォルダのUIと、同梱のESP-NOW v3固定配線ファームウェア。')
heading('構成図')
box(42,530,155,125,'Windows PC',['UI / WAV / STEP TXT','USBシリアル通信','Bluetooth音声出力'])
box(270,530,280,125,'統括・モーター基板',['XIAO ESP32C3','SLA7078へCLOCK / 方向出力','UART処理 + 40 kHzタイマー割り込み'])
arrow(197,590,270,590,'115200 bps')
box(270,370,280,105,'ライト基板',['XIAO ESP32C3 / ESP-NOW','一等星・恒星・星座8系統','最後の出力保持 / フェード処理'])
arrow(410,530,410,475,'ESP-NOW ch 1')
box(42,370,155,105,'Bluetoothスピーカー',['PC側で接続・出力先設定','マイコンは音声を扱わない'])
arrow(120,530,120,475,'音声')
y=340
heading('この版の変更')
para('こぐま座を系統5 / D5へ復元。上映TXTは104秒ON・149秒OFF。音声一時停止・終了時は速度0を即時送信し、定期送信・再接続後も停止を維持する。再開時に指令を再送する。')
para('COM機器名表示・応答による基板選択、スクロール対応、全STEP別窓、星座名編集を実装。出力ピンは固定で、light_mapping指令は送らない。旧基板で使うUI変更について新規書き込みは不要。')
heading('仕様の読み方')
para('本書はソースコードで確認できる動作を記述する。実機に書き込まれたファームウェアが同梱版と一致することを保証するものではない。モーター角度はパルス数による推定値であり、センサー測定値ではない。')

start('2. ハードウェアと固定配線')
heading('ライト基板')
table(['UI系統','端子','用途 / 点灯論理'],[['恒星','D0','LOWでON（active-low）'],['一等星','D1','HIGHでON'],['星座1','D7','未接続表示 / 操作は可能'],['星座2','D8','ペガスス座 / HIGHでON'],['星座3','D9','いて座 / HIGHでON'],['星座4','D10','さそり座 / HIGHでON'],['星座5','D5','こぐま座 / HIGHでON'],['星座6','D4','こいぬ座 / HIGHでON'],['星座7','D3','おおいぬ座 / HIGHでON'],['星座8','D2','オリオン座 / HIGHでON'],['状態LED','D6','正常:1秒ごと反転 / 切断:120msごと反転']],[100,65,345])
heading('統括・モーター基板')
table(['端子','SLA7078等への接続'],[['D0 / D1','MO入力 / M2'],['D2 / D3','CLOCK / 回転方向'],['D4 / D5','FLAG入力 / SYNC'],['D6 / D7','RESET / M3'],['D8 / D9 / D10','M1 / Ref・Sleep制御 / 状態LED']],[150,360])
para('モーター型番: PK296A10SG36（ユーザー指定:DC1.5A、2.2Ω）。コードの設定は減速比36、出力軸7200パルス/回転、1パルス約0.05°。最高速度定数300°/sはコード上の上限であり、実機で検証済みの速度ではない。',9)

start('3. モーター制御と停止動作')
heading('通常移動・角度管理')
para('現在角度は0°以上360°未満へ正規化する。通常目標も同範囲へ正規化し、現在位置から短い方向へ移動する。999は時計回り無限回転、-999は反時計回り無限回転。通常速度は絶対値で扱い、方向は目標または特殊角度で決まる。')
para('C3は単一コア。通信処理はFreeRTOSタスク、CLOCK生成は40kHzのハードウェアタイマー割り込みで行う。物理パルス数・原点オフセット・目標パルス数を保護して共有する。')
heading('原点・校正')
para('再起動後は原点未設定。通常の移動指令を受けても動かさず、UIに通知する。0°設定または現在角度設定により移動を許可する。校正画面には正負速度のジョグ、相対角度移動、停止、原点設定がある。音声再生中は校正画面を開けず、校正中は再生を拒否する。')
heading('停止条件')
table(['条件','動作'],[['音声一時停止・自然終了','UIが直ちに速度0を送信。停止ラッチにより後続送信も0。ライトは最後の指令を保持。'],['音声再開','停止ラッチ解除。現在STEPと有効な手動値を再送。'],['停止中の手動回転','速度上書きをONにし、速度入力後Enterで明示的に許可。'],['PC通信断','UIは3秒無応答で接続を閉じて再探索。基板ウォッチドッグはUI設定で3秒。'],['緊急停止','モーター停止・全ライトOFF。解除指令まで通常指令を禁止。'],['UI終了','停止指令を送信して接続を閉じる。送信不能時は基板ウォッチドッグに依存。']],[145,365])
heading('位置精度の限界')
para('脱調、バックラッシュ、手動で軸を動かした場合の誤差は検出できない。再起動時も実角度を保持しない。原点設定は運用者による位置合わせである。緊急停止はソフトウェア指令であり、電源遮断と同等ではない。')

start('4. 通信プロトコル・状態通知')
heading('PC - 統括基板（USB CDC / UART）')
para('115200bps。UTF-8 JSONを1行1メッセージとして改行で区切る。UIは受信断片をバッファへ蓄積し、改行が届いてから解析する。統括基板は送信ロックによりJSONの混在を防ぐ。')
table(['指令','意味'],[['set','motor.angle / speed、light.first / stars / patterns[8] / fadeを送信。'],['config','ESP送信周期、ACK待ち、最大再送回数、PCタイムアウトを設定。'],['ping','1秒間隔の生存確認。pongを受信。'],['motor_cal','jog_cw / jog_ccw / stop / move_relative / set_zero / set_angle / exit。'],['emergency_stop / release','緊急停止の開始 / 解除。'],['identify','UIの機器識別要求。同梱旧版は専用応答がないためstatusでも判別。']],[155,355])
para('全設定はデフォルト10秒間隔、変更時は即送信。統括からstatusは約250ms間隔で、起動後時間、原点・校正・停止状態、角度・速度、ライト通信状態等を返す。')
heading('統括 - ライト基板（ESP-NOW v3）')
para('Wi-Fi channel 1。統括MAC:02:50:4C:41:4E:01、ライトMAC:02:50:4C:41:4E:02。ペイロードにはmagic、version、type、size、seqを持つ。LIGHT_SETは一等星、恒星、星座8bit、fade、heartbeatTimeoutMsを含む。GPIO番号は送らず、基板内の固定対応で出力する。')
para('LIGHT_ACKは適用フラグ、ライト値、起動後時間を返す。同じseqのACKで受信確認する。定期送信は10秒、ACK待ちは0.5秒、初回に加え最大5回再送。再送中は不安定、上限超過で通信途絶を通知する。')
heading('COMポート選択・再接続')
para('COM番号と機器名を表示。更新時はUSBシリアル候補の応答を非同期で調べ、helloまたは統括固有statusで判別する。複数候補は手動選択可能。接続成功したUSBシリアル番号・VID/PID・COMを保存し、切断後は1秒間隔で再接続を試みる。接続時に再検証し、通信設定と全設定を再送する。')

start('5. ライト・音声・タイムライン')
heading('ライトの切替')
para('手動操作・強制送信は即時ON/OFF。音声再生中の通常STEP自動変更では約1.2秒のフェードを使う。滑らかな曲線 s=3p²-2p³ と s^1.8 で明るさを変える。途中の明るさはループによるパルス密度変調。0と255は固定出力としてちらつきを防ぐ。')
para('ライト基板は起動時に全OFF。統括との通信が切れても最後の指令を維持する。フェード途中なら最後の目標まで進む。状態LEDのみ高速点滅へ切り替える。監視期限はmax(3000ms, ESP周期×2+2000ms)。')
heading('音声・STEP制御')
para('WAVをPCで再生し、Bluetoothスピーカーへ出力する。UIは単調増加時計と再生基準時刻から再生位置を計算する。倍速は事前にピッチを維持したWAVを生成し、タイムラインも同じ速度で進める。Bluetoothの音声遅延は補正しないため、聞こえる音と制御の厳密な同時性は保証しない。')
para('再生バー、指定秒、前後STEP、先頭再生（確認付き）で移動する。全STEP一覧はスクロール可能で現STEPをハイライト。別窓一覧も使用可能。自動変更は初期ONで、OFF時に確認する。')
heading('TXTの形式')
para('UTF-8 CSV形式の.txt。#行はコメント。1行13列で、秒, 目標角度, 速度, 一等星, 恒星, 星座1〜8。ON/OFFまたは真偽値を使用。時刻で並べ替えて読む。星座名を変えても列番号の意味は変わらない。')
table(['列','内容'],[['1〜5','time_seconds / angle_deg / speed_deg_per_sec / first / stars'],['6〜9','D7 / D8ペガスス / D9いて / D10さそり'],['10〜13','D5こぐま / D4こいぬ / D3おおいぬ / D2オリオン']],[90,420])
para('例: 104,30,0.25,ON,ON,OFF,OFF,OFF,OFF,ON,OFF,OFF,OFF',9)
para('同梱の2024番組は104秒でこぐまON、149秒でOFF。旧GPIO19の指令を系統5/D5へ復元した。音声・TXTの保存先を記憶し、同梱の同名ファイルがあれば旧フォルダのものより優先する。')
heading('表示・保存')
para('ONは緑、OFFは赤。未通信の実機値は?付き。未反映の背景は赤、反映ランプは点滅。手動上書き背景は灰色。UARTとESP-NOWログは別欄で日時・再生位置を記録する。設定はAPPDATA/PlaneControl20260717/settings.jsonに保存する。')

start('6. 運用・保守・検証状況')
heading('上映前の手順')
para('1. 24V投入前に統括・モーター基板のUSB Type-CをPCへ接続する。\n2. 両基板へ24Vを投入する。\n3. 操作者用EXEを起動し、COMを更新・確認してUART接続する。\n4. 両通信が正常か確認し、WAVと上映TXTを選択する。\n5. Bluetoothスピーカーを接続し、音声出力先を確認する。\n6. 音声を停止したまま原点合わせを行い、通常制御へ戻る。\n7. 周囲を確認して再生する。終了後はモーター停止を確認する。')
heading('配布物・開発環境')
table(['場所','内容'],[['操作者用/','PlaneControl_v20261009-2.exe、統合WAV、上映TXT、説明書。'],['pc_ui/','Python UI、依存ライブラリ、EXE生成スクリプト、停止テスト。'],['firmware/coordinator/','XIAO ESP32C3用PlatformIOプロジェクト。'],['firmware/light_controller/','ライト用XIAO ESP32C3プロジェクト。'],['firmware/common/','ESP-NOW v3共有定義。'],['docs/・output/pdf/','説明資料・本仕様書。']],[165,345])
heading('確認済みと未確認')
para('確認済み: ソースの構文・UI起動、800×480/1366×600でのレイアウト、こぐま座104/149秒の指令、999/-999の停止ラッチと再開のハードウェア非接続テスト。')
para('未確認: 今回の停止修正の実機試験、全PCでのCOM自動検出、Bluetooth実音声との時間差、最高回転速度、実際に書き込み済みの基板バージョン。今回ファームウェアのコンパイル・書き込みは実施していない。')
heading('実装上の注意・残る制約')
para('ライト現在値はGPIO電圧や実際の発光の測定値ではない。統括statusのライト値には指令値が含まれ、ACK通信状態とあわせて判断する。ACK appliedはフェード完了の確認ではない。シリアル送信に失敗した停止指令は即時到達を保証できない。')
para('ステッピングモーターはセンサーによる閉ループ制御ではない。校正ジョグ中のUI異常終了はPCウォッチドッグの停止に依存する。再接続時に音声が再生中なら、その時点の指令でモーターが再開しうる。')
heading('参照ソース')
para('pc_ui/app.py、pc_ui/test_pause.py、firmware/coordinator/src/main.cpp、firmware/coordinator/platformio.ini、firmware/light_controller/src/main.cpp、firmware/common/protocol.h、操作者用/2024番組_指示送信設定.txt。',9)
c.save()
print(OUT)
