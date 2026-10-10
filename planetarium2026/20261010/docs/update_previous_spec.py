"""Keep the previous nine-page specification layout; replace changed content."""
from pathlib import Path
from io import BytesIO
import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

root=Path(__file__).resolve().parents[1]
source=root/'システム仕様書_v20260716.pdf'
target=root/'output/pdf/システム仕様書_v20261009-2.pdf'
pdfmetrics.registerFont(TTFont('JP',r'C:\Windows\Fonts\msgothic.ttc',subfontIndex=0))
reader=PdfReader(source); writer=PdfWriter(); parsed=pdfplumber.open(source)
W,H=595.28,841.89
def wrap(text,size,width):
 out=[]
 for para in text.split('\n'):
  line=''
  for ch in para:
   if line and pdfmetrics.stringWidth(line+ch,'JP',size)>width:out.append(line);line=ch
   else:line+=ch
  out.append(line)
 return out
def text(c,x,top,text,size=9,color='#25374b',width=505):
 c.setFillColor(HexColor(color));c.setFont('JP',size)
 for line in wrap(text,size,width):c.drawString(x,H-top-size,line);top+=size*1.5
 return top
def erase(c,x,top,w,h,color='#ffffff'):
 c.setFillColor(HexColor(color));c.rect(x,H-top-h,w,h,stroke=0,fill=1)
def find(page,pattern):
 matches=page.search(pattern)
 if not matches:raise ValueError(pattern)
 return matches[0]
def replace_line(c,page,pattern,replacement,size=9,bg='#ffffff',width=515):
 m=find(page,pattern);erase(c,m['x0']-1,m['top']-2,width,size*1.8,bg);text(c,m['x0'],m['top']-1,replacement,size,width=width)
def block(c,top,title,body):
 height=29+len(wrap(body,9,505))*13.5
 erase(c,36,top,522,min(height,798-top))
 c.setFillColor(HexColor('#2f75b5'));c.roundRect(36,H-top-15,4,17,2,fill=1,stroke=0)
 text(c,49,top-1,title,12,color='#14273e')
 return text(c,49,top+25,body,9,width=505)

for i,page in enumerate(reader.pages):
 data=BytesIO();c=canvas.Canvas(data,pagesize=(W,H));p=parsed.pages[i]
 if i==0:
  replace_line(c,p,'文書版.*','文書版：v20261009-2 / 2026-10-09',10,bg='#15263a')
  # Cover labels use white type on the original dark surface.
  for pattern,value in [('文書版.*','文書版：v20261009-2 / 2026-10-09'),('対象フォルダ.*','対象フォルダ：プラネ（ローカル） / 20261009-2')]:
   m=find(p,pattern);erase(c,48,m['top']-2,505,18,'#15263a');text(c,50,m['top']-1,value,10,color='#ffffff')
 else:
  erase(c,35,803,490,20);text(c,36,806,'プラネタリウム統合制御 システム仕様書 v20261009-2',8,color='#73879b')
 if i==1:
  replace_line(c,p,'SLA7078＋PK296A1-SG36','SLA7078＋PK296A10SG36',9,width=220)
  block(c,700,'20261009-2 更新概要','既存の固定配線・ESP-NOW v3を維持。こぐま座（D5）を復元し、音声一時停止・終了時のモーター停止を追加。COM自動選択と小画面対応を追加。基板への新規書き込みは不要。')
 if i==2:
  m=find(p,'要求値と実機値が一致しない.*');erase(c,48,m['top']-2,510,18);text(c,49,m['top']-1,'・未反映の背景は赤の固定表示、反映インジケータは赤く点滅する。',9)
  block(c,635,'画面サイズ・星座名・上映データの更新','全系統は縦横スクロールで操作できる。全STEP一覧は別ウィンドウでも表示可能。星座名は設定から編集でき、ピンは固定。系統5＝D5こぐま座。2024番組は104秒ON、149秒OFF。最新版の同梱TXTを優先して読み込む。')
 if i==3:
  block(c,645,'COMポート選択とUART復旧','COM番号に機器名を併記。更新時はUSB候補の応答を調べ、統括固有のstatusでも識別する。手動選択も可能。接続成功した機器を保存し、切断・3秒無応答時は1秒間隔で再接続する。再接続後は設定再送。一時停止中の速度は0のまま維持する。UARTの行受信をバッファ化し、送信競合を防ぐ。')
 if i==4:
  replace_line(c,p,'PK296A1-SG36','PK296A10SG36',12,bg='#f0eef9',width=220)
 if i==5:
  block(c,695,'固定配線版の互換性','本版はVersion 3を継続する。UIはGPIO番号を送らず、星座8bitのON/OFFを送る。別版v20261004-2の動的ピン変更（Version 4）は本版では使用しない。こぐま座D5は従来の系統5として動作する。')
 if i==6:
  replace_line(c,p,'通常点滅 / 切断時高速点滅','正常は低速 / 切断は高速点滅',8,width=150)
  block(c,690,'星座名対応・通信断時の動作','D7：予備、D8：ペガスス、D9：いて、D10：さそり、D5：こぐま、D4：こいぬ、D3：おおいぬ、D2：オリオン。通信断でも最後の指令を保持（フェード中なら目標まで継続）。完全ON/OFFは固定出力とし、PWMによる瞬間消灯を防ぐ。')
 if i==7:
  block(c,700,'音声停止・再開と校正の追加制御','音声一時停止・終了時に速度0を即時送信。停止ラッチにより定期送信や再接続でも停止を維持。再生時に現在STEPを再送。停止中の手動回転は速度上書き＋入力後Enterで許可。校正中・緊急停止中は音声再生を拒否する。UI終了時にも停止を送る。')
 if i==8:
  block(c,660,'配布版・検証状況','操作者用/PlaneControl_v20261009-2.exeと同梱WAV・修正済みTXTを使用する。UI起動、こぐま104秒ON/149秒OFF、999/-999の停止ラッチ・再開を非接続テストで確認。今回の停止修正の実機試験と、基板へのコンパイル・書き込みは未実施。角度とライト値は実測ではない。')
 c.save();data.seek(0);page.merge_page(PdfReader(data).pages[0]);writer.add_page(page)
writer.add_metadata({'/Title':'プラネタリウム統合制御 システム仕様書 v20261009-2','/Author':'TokyoTech-Astro Planetarium Project'})
with target.open('wb') as f:writer.write(f)
print(target)
