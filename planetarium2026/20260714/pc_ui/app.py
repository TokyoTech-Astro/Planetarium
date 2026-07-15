import bisect, csv, ctypes, hashlib, json, os, queue, sys, threading, time, wave
from datetime import datetime, timedelta
from pathlib import Path
VENDOR = Path(__file__).with_name("vendor")
if VENDOR.exists(): sys.path.insert(0, str(VENDOR))
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from audiostretchy.stretch import stretch_audio

try:
    import serial
    from serial.tools import list_ports
except Exception:
    serial = None
try:
    import pygame
except Exception:
    pygame = None

APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "PlaneControl20260713"
SETTINGS = APP_DIR / "settings.json"
BG, PANEL, CARD, TEXT, MUTED = "#0b0f14", "#121923", "#182231", "#ecf2fa", "#8ca0b8"
GREEN, RED, ORANGE, BLUE, OFF = "#2bd576", "#ff4d67", "#ff9f43", "#4da3ff", "#526170"
HELP_BLUE = "#315b82"
FIELDS = ["angle", "speed", "first", "stars"] + [f"p{i}" for i in range(1, 9)]
LABELS = {"angle":"目標角度 (°)","speed":"回転速度 (°/s)","first":"一等星","stars":"恒星","p1":"さそり座","p2":"ペガサス座","p3":"おおいぬ座","p4":"こいぬ座","p5":"こぐま座","p6":"オリオン座","p7":"いて座","p8":"未使用"}

def as_bool(s): return str(s).strip().lower() in ("1","true","on","yes","はい")
def defaults(): return {"angle":0.0,"speed":0.0,"first":False,"stars":False,**{f"p{i}":False for i in range(1,9)}}
def fmt_time(sec):
    sec=max(0,float(sec)); return f"{int(sec//60):02d}:{sec%60:05.2f}"
def fmt_uptime(sec):
    sec=max(0,int(sec));days,sec=divmod(sec,86400);hours,sec=divmod(sec,3600);minutes,seconds=divmod(sec,60)
    return f"{days}日 {hours:02d}:{minutes:02d}:{seconds:02d}" if days else f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def default_output_name():
    try:
        if pygame is not None:
            if not pygame.mixer.get_init():pygame.mixer.init()
            from pygame._sdl2 import audio as sdl_audio
            names=sdl_audio.get_audio_device_names(False)
            if names:return names[0]
    except Exception:pass
    if os.name!="nt":return "既定の音声出力"
    class WaveOutCaps(ctypes.Structure):
        _fields_=[("wMid",ctypes.c_ushort),("wPid",ctypes.c_ushort),("vDriverVersion",ctypes.c_uint),("szPname",ctypes.c_wchar*32),("dwFormats",ctypes.c_uint),("wChannels",ctypes.c_ushort),("wReserved1",ctypes.c_ushort),("dwSupport",ctypes.c_uint)]
    try:
        caps=WaveOutCaps();fn=ctypes.windll.winmm.waveOutGetDevCapsW;fn.argtypes=[ctypes.c_size_t,ctypes.POINTER(WaveOutCaps),ctypes.c_uint];fn.restype=ctypes.c_uint;result=fn(ctypes.c_size_t(-1),ctypes.byref(caps),ctypes.sizeof(caps));return caps.szPname if result==0 and caps.szPname else "Windows既定の音声出力"
    except Exception:return "Windows既定の音声出力"

def load_timeline(path):
    rows=[]
    with open(path,"r",encoding="utf-8-sig") as f:
        for raw in f:
            if not raw.strip() or raw.lstrip().startswith("#"): continue
            a=next(csv.reader([raw]));
            if len(a)!=13: raise ValueError(f"列数は13必要です: {raw.strip()}")
            v=defaults(); v["angle"]=float(a[1]);v["speed"]=float(a[2]);v["first"]=as_bool(a[3]);v["stars"]=as_bool(a[4])
            for i in range(8):v[f"p{i+1}"]=as_bool(a[5+i])
            rows.append({"time":float(a[0]),**v})
    if not rows: raise ValueError("イベントがありません")
    return sorted(rows,key=lambda x:x["time"])

def save_timeline(path, rows):
    with open(path,"w",encoding="utf-8",newline="") as f:
        f.write("# PlaneControl Timeline v1\n# time_seconds,angle_deg,speed_deg_per_sec,first_star,stars,constellation1..constellation8\n")
        w=csv.writer(f,lineterminator="\n")
        for r in sorted(rows,key=lambda x:x["time"]):w.writerow([f'{r["time"]:.3f}',r["angle"],r["speed"],*("ON" if r[k] else "OFF" for k in ["first","stars"]+[f"p{i}" for i in range(1,9)])])

class Led(tk.Canvas):
    def __init__(self,parent,size=16):
        super().__init__(parent,width=size,height=size,bg=parent.cget("bg"),highlightthickness=0);self.dot=self.create_oval(2,2,size-2,size-2,fill=OFF,outline="")
    def set(self,color):self.itemconfigure(self.dot,fill=color)

class App:
    def __init__(self,root):
        self.root=root;root.title("プラネ統合制御 20260714");root.geometry("1480x900");root.minsize(1180,760);root.configure(bg=BG)
        self.ttk_style=ttk.Style(root)
        try:self.ttk_style.theme_use("clam")
        except tk.TclError:pass
        self.ttk_style.configure("Dark.Treeview",background="#101821",fieldbackground="#101821",foreground="#dce8f5",bordercolor="#26384b",lightcolor="#26384b",darkcolor="#26384b",borderwidth=1,rowheight=24)
        self.ttk_style.configure("Dark.Treeview.Heading",background="#253349",foreground="#f2f7fc",bordercolor="#3a4d66",lightcolor="#3a4d66",darkcolor="#172130",relief="flat",font=("Yu Gothic UI",9,"bold"))
        self.ttk_style.map("Dark.Treeview",background=[("selected","#0875c1")],foreground=[("selected","#ffffff")]);self.ttk_style.map("Dark.Treeview.Heading",background=[("active","#30445f")],foreground=[("active","#ffffff")])
        self.ttk_style.configure("Editor.TCombobox",fieldbackground="#101821",background="#253349",foreground="#ffffff",arrowcolor="#ffffff",bordercolor="#0875c1",lightcolor="#0875c1",darkcolor="#0875c1");self.ttk_style.map("Editor.TCombobox",fieldbackground=[("readonly","#101821")],foreground=[("readonly","#ffffff")],selectbackground=[("readonly","#0875c1")],selectforeground=[("readonly","#ffffff")]);root.option_add("*TCombobox*Listbox.background","#101821");root.option_add("*TCombobox*Listbox.foreground","#ffffff");root.option_add("*TCombobox*Listbox.selectBackground","#0875c1")
        for orient in ("Vertical","Horizontal"):self.ttk_style.configure(f"Dark.{orient}.TScrollbar",background="#34475a",troughcolor="#101821",bordercolor="#101821",arrowcolor="#eaf2fa",lightcolor="#34475a",darkcolor="#34475a")
        APP_DIR.mkdir(parents=True,exist_ok=True);self.cfg=self.load_cfg();self.timeline=[];self.timeline_times=[];self.audio="";self.duration=0;self.playing=False;self.play_origin=0;self.seek_base=0;self.rate=1.0
        self.ser=None;self.rx=queue.Queue();self.last_pc=None;self.uart_health="disconnected";self.uart_connected_at=None;self.last_speaker_check=0;self.output_device=default_output_name();self.scrub_was_playing=False;self.motor_calibration_mode=False;self.motor_origin_set=False;self.motor_motion="stopped";self.motor_target_angle=0.0;self.mcu_uptime={"pc":0.0,"light":0.0};self.calibration_window=None;self.links={"motor":{"last":None,"remote_ack":0,"online":False,"unstable":False},"light":{"last":None,"remote_ack":0,"online":False,"unstable":False}}
        self.desired=defaults();self.actual=defaults();self.override={k:tk.BooleanVar(value=False) for k in FIELDS};self.manual={k:tk.StringVar(value="0" if k in ("angle","speed") else "OFF") for k in FIELDS}
        self.auto=tk.BooleanVar(value=True);self.step_jump_enabled=tk.BooleanVar(value=True);self.vars={};self.last_sent=None;self.flash=False;self.last_flash_at=time.monotonic();self.current_step_shown=None;self.nav_step_index=None;self.nav_step_at=0;self.step_value_labels=[];self.refreshing_step_colors=False;self.step_color_job=None;self.build();self.restore();self.root.after(100,self.tick);self.root.protocol("WM_DELETE_WINDOW",self.close)
        self.rate_results=queue.Queue();self.rate_conversion_active=False;self.last_keepalive=0.0;self.emergency_stop=False
    def load_cfg(self):
        try:return json.loads(SETTINGS.read_text(encoding="utf-8"))
        except:return {"uart_interval":10.0,"esp_interval":10.0,"retry_timeout":0.5,"max_retries":5}
    def save_cfg(self):
        self.cfg.update({"audio":self.audio,"timeline":getattr(self,"timeline_path","")});SETTINGS.write_text(json.dumps(self.cfg,ensure_ascii=False,indent=2),encoding="utf-8")
    def frame(self,parent,**kw):return tk.Frame(parent,bg=kw.pop("bg",PANEL),**kw)
    def label(self,parent,text="",**kw):return tk.Label(parent,text=text,bg=kw.pop("bg",parent.cget("bg")),fg=kw.pop("fg",TEXT),font=kw.pop("font",("Yu Gothic UI",10)),**kw)
    def button(self,parent,text,cmd,**kw):return tk.Button(parent,text=text,command=cmd,bg=kw.pop("bg","#253349"),fg=TEXT,activebackground=BLUE,activeforeground="white",relief="flat",font=("Yu Gothic UI",10,"bold"),padx=kw.pop("padx",10),pady=kw.pop("pady",6),**kw)
    def show_help_window(self,title,content,parent=None):
        w=tk.Toplevel(parent or self.root);w.title(title);w.geometry("760x620");w.configure(bg=BG);box=tk.Text(w,bg="#101821",fg=TEXT,insertbackground=TEXT,wrap="word",relief="flat",font=("Yu Gothic UI",10),padx=18,pady=14);scroll=ttk.Scrollbar(w,orient="vertical",command=box.yview);box.configure(yscrollcommand=scroll.set);box.pack(side="left",fill="both",expand=True,padx=(12,0),pady=12);scroll.pack(side="right",fill="y",padx=(0,12),pady=12);box.insert("1.0",content);box.config(state="disabled")
    def show_main_help(self):
        self.show_help_window("プラネ統合制御の使い方","""【基本操作】
1. 統括・モーターC3とPCをUSB接続し、COMポートを選んでUART接続します。
2. 音声ファイルとタイムラインTXTを選択します。
3. 再生ボタンで音声と自動制御を開始します。

【角度】
角度は0°以上360°未満で管理します。目標角度999は時計回り、-999は反時計回りの無限回転です。再起動後は原点未設定になるため、音声を停止して「モーター0°位置設定」を実行してください。

【手動上書き】
上書きをONにすると、その系統だけタイムライン設定より手動値を優先します。「今すぐ全設定を送信」で直ちに送信できます。

【表示】
緑は正常、オレンジは不安定、赤は未接続・未反映です。実機値に?が付く場合は現在値を確認できていません。

【指示送信設定】
右上の「指示送信設定」からSTEPを編集します。詳しい操作は設定画面内の「使い方」を確認してください。""")
    def build(self):
        top=self.frame(self.root,bg=BG);top.pack(fill="x",padx=14,pady=(12,8));self.label(top,"プラネ統合制御",bg=BG,font=("Yu Gothic UI",20,"bold")).pack(side="left")
        self.port=tk.StringVar();self.portbox=ttk.Combobox(top,textvariable=self.port,width=15,state="readonly");self.portbox.pack(side="left",padx=(30,6));self.button(top,"更新",self.refresh_ports).pack(side="left");self.connect_btn=self.button(top,"UART接続",self.toggle_serial,bg=BLUE);self.connect_btn.pack(side="left",padx=6);self.button(top,"設定",self.settings_dialog).pack(side="right");self.button(top,"使い方",self.show_main_help,bg=HELP_BLUE).pack(side="right",padx=6)
        self.estop_btn=self.button(top,"緊急停止",self.activate_emergency_stop,bg="#c62828",padx=18,pady=9);self.estop_btn.pack(side="right",padx=12)
        self.estop_banner=self.label(self.root,"",bg=BG,fg="white",font=("Yu Gothic UI",14,"bold"),anchor="center")
        status=self.frame(self.root);status.pack(fill="x",padx=14,pady=4);self.status_widgets={}
        for key,title in (("pc","PC ↔ 統括・モーター"),("light","統括 ↔ ライト")):
            c=self.frame(status,bg=CARD);c.pack(side="left",fill="x",expand=True,padx=5,pady=6);led=Led(c,18);led.pack(side="left",padx=12,pady=10);v=self.label(c,title,bg=CARD,font=("Yu Gothic UI",11,"bold"));v.pack(anchor="w",pady=(6,0));age=self.label(c,"最終通信: --",bg=CARD,fg=MUTED,font=("Yu Gothic UI",8));age.pack(anchor="w",pady=(0,6));self.status_widgets[key]=(c,led,v,age)
        self.workspace=tk.PanedWindow(self.root,orient="vertical",bg="#27364a",sashwidth=7,sashrelief="flat",borderwidth=0);self.workspace.pack(fill="both",expand=True,padx=14,pady=(0,12));body=self.frame(self.workspace,bg=BG);left=self.frame(body);left.pack(side="left",fill="both",expand=True,padx=(0,5));right=self.frame(body);right.pack(side="right",fill="both",expand=True,padx=(5,0));log_area=self.frame(self.workspace,bg=BG)
        self.workspace.add(body,minsize=390,stretch="always");self.workspace.add(log_area,minsize=115,stretch="never");self.build_values(left);self.build_audio(right);self.build_log(log_area);self.root.after_idle(lambda:self.workspace.sash_place(0,0,max(390,self.root.winfo_height()-300)))
    def build_values(self,parent):
        h=self.frame(parent);h.pack(fill="x",padx=8,pady=8);self.label(h,"制御値 / 反映状態",font=("Yu Gothic UI",13,"bold")).pack(side="left");self.origin_status=self.label(h,"原点未設定：モーター移動禁止",bg="#54202a",fg="#ffb6bd",font=("Yu Gothic UI",10,"bold"));self.origin_status.pack(side="left",padx=12,ipadx=8,ipady=3);self.button(h,"今すぐ全設定を送信",lambda:self.send(True),bg=BLUE).pack(side="right");self.button(h,"モーター0°位置設定",self.open_motor_calibration,bg=ORANGE).pack(side="right",padx=6)
        self.label(parent,"※ 目標角度 999＝時計回り無限回転、-999＝反時計回り無限回転",fg="#9ec7ef",font=("Yu Gothic UI",8)).pack(anchor="w",padx=12,pady=(0,3))
        grid=self.frame(parent);grid.pack(fill="both",expand=True,padx=8)
        for col,t in enumerate(("系統","要求設定値","実機現在値","反映","上書き","手動値")):self.label(grid,t,fg=MUTED).grid(row=0,column=col,sticky="ew",padx=5,pady=4)
        grid.columnconfigure(0,weight=2);grid.columnconfigure(1,weight=1);grid.columnconfigure(2,weight=1);grid.columnconfigure(5,weight=1)
        for row,k in enumerate(FIELDS,1):
            box=self.frame(grid,bg=CARD);box.grid(row=row,column=0,columnspan=6,sticky="nsew",pady=2);box.lower()
            name=self.label(grid,LABELS[k],bg=CARD);name.grid(row=row,column=0,sticky="w",padx=10,pady=6)
            req=tk.StringVar(value="--");act=tk.StringVar(value="--");req_label=self.label(grid,textvariable=req,bg=CARD);req_label.grid(row=row,column=1);act_label=self.label(grid,textvariable=act,bg=CARD);act_label.grid(row=row,column=2)
            led=Led(grid);led.configure(bg=CARD);led.grid(row=row,column=3)
            cb=tk.Checkbutton(grid,variable=self.override[k],command=self.on_override,bg=CARD,activebackground=CARD,selectcolor=PANEL,fg=TEXT);cb.grid(row=row,column=4)
            control=None
            if k in ("angle","speed"):control=tk.Entry(grid,textvariable=self.manual[k],width=10,bg="#0e151e",fg=TEXT,insertbackground=TEXT,relief="flat");control.bind("<Return>",lambda e:self.manual_changed());control.grid(row=row,column=5,padx=7)
            else:
                control=self.button(grid,"OFF",lambda key=k:self.toggle_manual(key),pady=2);control.grid(row=row,column=5);self.manual[k].trace_add("write",lambda *_args,key=k,btn=control:btn.config(text=self.manual[key].get()))
            self.vars[k]={"req":req,"act":act,"led":led,"box":box,"name":name,"req_label":req_label,"act_label":act_label,"check":cb,"control":control}
    def build_audio(self,parent):
        h=self.frame(parent);h.pack(fill="x",padx=8,pady=8);self.label(h,"音声・タイムライン",font=("Yu Gothic UI",13,"bold")).pack(side="left");self.button(h,"指示送信設定",self.timeline_editor).pack(side="right")
        files=self.frame(parent,bg=CARD);files.pack(fill="x",padx=8,pady=3);info=self.frame(files,bg=CARD);info.pack(side="left",fill="x",expand=True,padx=8,pady=4);self.audio_label=self.label(info,"音声: 未選択",bg=CARD,fg=MUTED,anchor="w");self.audio_label.pack(anchor="w");self.speaker_label=self.label(info,"出力スピーカー: "+self.output_device,bg=CARD,fg="#9ec7ef",anchor="w",font=("Yu Gothic UI",8));self.speaker_label.pack(anchor="w");self.button(files,"音声選択",self.choose_audio).pack(side="right",padx=3,pady=5);self.button(files,"TXT読込",self.choose_timeline).pack(side="right",padx=3);self.button(files,"↻ 最初から再生",self.restart_from_beginning,padx=7,bg=RED).pack(side="right",padx=3)
        self.next_label=self.label(parent,"次の変更: --",fg="#ffd38a",anchor="w",justify="left");self.next_label.pack(fill="x",padx=12,pady=7)
        self.pos=tk.DoubleVar();self.scale=ttk.Scale(parent,from_=0,to=1,variable=self.pos,command=self.seek_preview);self.scale.pack(fill="x",padx=12);self.scale.bind("<ButtonPress-1>",self.begin_scrub);self.scale.bind("<ButtonRelease-1>",self.end_scrub);self.time_label=self.label(parent,"00:00.00 / 00:00.00");self.time_label.pack()
        controls=self.frame(parent);controls.pack(fill="x",padx=8,pady=8);self.play_btn=self.button(controls,"▶  再生",self.toggle_play,bg=GREEN);self.play_btn.pack(side="left",ipadx=14,ipady=10);self.button(controls,"◀ 前のステップ",lambda:self.jump_event(-1),padx=6).pack(side="left",padx=2);self.button(controls,"次のステップ ▶",lambda:self.jump_event(1),padx=6).pack(side="left",padx=2)
        self.rate_var=tk.StringVar(value="1.0x");rates=ttk.Combobox(controls,textvariable=self.rate_var,values=["0.5x","0.75x","1.0x","1.25x","1.5x","2.0x"],width=5,state="readonly");rates.pack(side="left",padx=3);rates.bind("<<ComboboxSelected>>",self.change_rate);self.jump_var=tk.StringVar(value="0");tk.Entry(controls,textvariable=self.jump_var,width=6,bg="#0e151e",fg=TEXT,insertbackground=TEXT,relief="flat").pack(side="left",padx=(3,1),ipady=5);self.button(controls,"指定秒へ",self.jump_seconds,padx=5).pack(side="left",padx=1);self.end_label=self.label(controls,"残り -- / 予定 --",fg=MUTED,font=("Yu Gothic UI",8));self.end_label.pack(side="right",padx=4)
        auto=self.frame(parent,bg=CARD);auto.pack(fill="x",padx=8,pady=6);self.auto_cb=tk.Checkbutton(auto,text="再生時間による設定値自動変更",variable=self.auto,command=self.auto_changed,bg=CARD,fg=TEXT,activebackground=CARD,activeforeground=TEXT,selectcolor=PANEL,font=("Yu Gothic UI",10,"bold"));self.auto_cb.pack(side="left",padx=8,pady=8)
        overview=self.frame(parent,bg=CARD);overview.pack(fill="both",expand=True,padx=8,pady=(3,8));ov_head=self.frame(overview,bg=CARD);ov_head.pack(fill="x",padx=8,pady=(6,3));self.label(ov_head,"全STEP一覧",bg=CARD,font=("Yu Gothic UI",10,"bold")).pack(side="left");self.label(ov_head,"999＝時計回り／-999＝反時計回り 無限回転",bg=CARD,fg="#9ec7ef",font=("Yu Gothic UI",8)).pack(side="left",padx=12);self.step_jump_btn=self.button(ov_head,"ダブルクリック移動: ON",self.toggle_step_jump,bg="#265f43",pady=2);self.step_jump_btn.pack(side="right")
        table=self.frame(overview,bg=CARD);table.pack(fill="both",expand=True,padx=7,pady=(0,7));cols=("step","time")+tuple(FIELDS);self.step_tree=ttk.Treeview(table,columns=cols,show="headings",height=7,selectmode="none",style="Dark.Treeview")
        for c in cols:
            title="STEP" if c=="step" else "秒" if c=="time" else LABELS[c].replace(" (°)","").replace(" (°/s)","");self.step_tree.heading(c,text=title);self.step_tree.column(c,width=68 if c not in ("angle","speed") else 90,anchor="center",stretch=False)
        sy=ttk.Scrollbar(table,orient="vertical",command=self.scroll_step_y,style="Dark.Vertical.TScrollbar");sx=ttk.Scrollbar(table,orient="horizontal",command=self.scroll_step_x,style="Dark.Horizontal.TScrollbar");self.step_tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);self.step_tree.grid(row=0,column=0,sticky="nsew");sy.grid(row=0,column=1,sticky="ns");sx.grid(row=1,column=0,sticky="ew");table.rowconfigure(0,weight=1);table.columnconfigure(0,weight=1);self.step_tree.tag_configure("current",background="#34475a",foreground="#ffffff");self.step_tree.bind("<Double-1>",self.on_step_double_click);self.step_tree.bind("<MouseWheel>",self.on_step_mousewheel);self.step_tree.bind("<Configure>",lambda _e:self.schedule_step_value_colors())
    def build_log(self,parent):
        f=self.frame(parent);f.pack(fill="both",expand=True);head=self.frame(f);head.pack(fill="x",padx=8);self.label(head,"通信イベントログ",font=("Yu Gothic UI",11,"bold")).pack(side="left");self.label(head,"上の境界線をドラッグして高さ調整",fg=MUTED,font=("Yu Gothic UI",8)).pack(side="right");panes=self.frame(f);panes.pack(fill="both",expand=True,padx=8,pady=(2,8));self.logboxes={}
        for key,title in (("uart","PC ↔ 統括マイコン（UART）"),("mcu","統括マイコン ↔ 制御マイコン（ESP-NOW）")):
            pane=self.frame(panes,bg=CARD);pane.pack(side="left",fill="both",expand=True,padx=(0,4) if key=="uart" else (4,0));self.label(pane,title,bg=CARD,fg=MUTED,font=("Yu Gothic UI",9,"bold")).pack(anchor="w",padx=7,pady=(5,2));body=self.frame(pane,bg=CARD);body.pack(fill="both",expand=True,padx=5,pady=(0,5));box=tk.Text(body,height=7,bg="#080c11",fg="#b9c7d8",insertbackground=TEXT,relief="flat",font=("Consolas",9),wrap="word");scroll=ttk.Scrollbar(body,orient="vertical",command=box.yview);box.configure(yscrollcommand=scroll.set);box.pack(side="left",fill="both",expand=True);scroll.pack(side="right",fill="y");self.logboxes[key]=box
    def log(self,msg,channel="uart"):
        box=self.logboxes.get(channel,self.logboxes["uart"]);box.insert("end",f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [再生 {fmt_time(self.position())}] {msg}\n");box.see("end")
    def restore(self):
        self.refresh_ports()
        for kind,fn in (("audio",self.load_audio),("timeline",self.load_timeline_file)):
            p=self.cfg.get(kind,"")
            if p and Path(p).exists():
                try:fn(p)
                except Exception as e:self.log(f"前回の{kind}を読めません: {e}")
        if not self.timeline:
            p=Path(__file__).with_name("sample_timeline.txt")
            if p.exists():self.load_timeline_file(str(p))
    def refresh_ports(self):
        ports=[p.device for p in list_ports.comports()] if serial else [];self.portbox["values"]=ports
        if ports and self.port.get() not in ports:self.port.set(ports[0])
    def toggle_serial(self):
        if self.ser:
            self.ser.close();self.ser=None;self.uart_health="disconnected";self.uart_connected_at=None;self.connect_btn.config(text="UART接続",bg=BLUE);self.log("UARTを切断")
        else:
            try:self.ser=serial.Serial(self.port.get(),115200,timeout=.2);self.last_pc=None;self.uart_health="waiting";self.uart_connected_at=time.monotonic();threading.Thread(target=self.reader,daemon=True).start();self.connect_btn.config(text="切断",bg=RED);self.log(f"UART接続 {self.port.get()}");self.configure_mcu();self.send(True)
            except Exception as e:self.log(f"UART接続失敗 {self.port.get()}: {e}");messagebox.showerror("接続エラー",str(e));self.ser=None;self.uart_health="disconnected"
    def reader(self):
        while self.ser and self.ser.is_open:
            try:
                s=self.ser.readline().decode("utf-8","replace").strip()
                if s:self.rx.put(json.loads(s))
            except json.JSONDecodeError:self.rx.put({"type":"bad_line","line":s[:160]})
            except Exception as e:self.rx.put({"type":"serial_error","error":str(e)});break
    def write(self,obj):
        if not self.ser or not self.ser.is_open:return False
        try:self.ser.write((json.dumps(obj,separators=(",",":"))+"\n").encode());return True
        except Exception as e:self.log(f"UART送信失敗: {e}");self.uart_health="failed";return False
    def configure_mcu(self):
        pc_timeout=3000
        self.write({"cmd":"config","esp_interval_ms":int(self.cfg["esp_interval"]*1000),"retry_timeout_ms":int(self.cfg["retry_timeout"]*1000),"max_retries":int(self.cfg["max_retries"]),"pc_timeout_ms":pc_timeout})
    def effective(self):
        d=dict(self.desired)
        for k in FIELDS:
            if self.override[k].get():d[k]=float(self.manual[k].get()) if k in ("angle","speed") else as_bool(self.manual[k].get())
        if abs(abs(d["angle"])-999.0)>=.01:d["angle"]=d["angle"]%360.0
        return d
    def send(self,force=False,fade=False):
        if self.emergency_stop:return
        try:d=self.effective()
        except ValueError:self.log("手動値が数値ではありません");return
        if not force and d==self.last_sent:return
        if self.write({"cmd":"set","motor":{"angle":d["angle"],"speed":d["speed"]},"light":{"first":d["first"],"stars":d["stars"],"patterns":[d[f"p{i}"] for i in range(1,9)],"fade":bool(fade)}}):self.last_sent=d
        self.update_values()
    def activate_emergency_stop(self):
        if self.emergency_stop:
            self.release_emergency_stop();return
        self.emergency_stop=True;self.update_emergency_stop_display()
        sent=self.write({"cmd":"emergency_stop"})
        self.log("緊急停止を実行：モーター停止、全ライトOFF")
        if not sent:messagebox.showerror("緊急停止通信エラー","緊急停止指令をUARTへ送信できませんでした。直ちに24V電源を切ってください。")
    def release_emergency_stop(self):
        if not messagebox.askyesno("緊急停止を解除","周囲の安全を確認しましたか？\n緊急停止を解除すると、現在の設定値が再送信されます。"):
            return
        if not self.write({"cmd":"emergency_stop_release"}):
            messagebox.showerror("解除できません","統括・モーター基板と通信できません。緊急停止は解除されていません。");return
        self.emergency_stop=False;self.update_emergency_stop_display();self.root.after(150,lambda:self.send(True));self.log("緊急停止を解除")
    def update_emergency_stop_display(self):
        if self.emergency_stop:
            self.estop_btn.config(text="緊急停止解除",bg="#ef6c00")
            self.estop_banner.config(text="⚠ 緊急停止中：モーター停止・全ライトOFF　安全確認後に『緊急停止解除』を押してください",bg="#b71c1c")
            if not self.estop_banner.winfo_manager():self.estop_banner.pack(fill="x",padx=14,pady=(0,6),ipady=9,before=self.workspace)
        else:
            self.estop_btn.config(text="緊急停止",bg="#c62828")
            if self.estop_banner.winfo_manager():self.estop_banner.pack_forget()
    def process(self,d):
        t=d.get("type")
        if t in ("event","status","hello","pong"):self.last_pc=time.monotonic()
        if t=="event":self.log(f'{d.get("device","")} {d.get("event","")}',"mcu")
        elif t=="status":
            reported_estop=bool(d.get("emergency_stop",False))
            if reported_estop!=self.emergency_stop:self.emergency_stop=reported_estop;self.update_emergency_stop_display()
            self.motor_calibration_mode=bool(d.get("motor_calibration_mode",False));self.motor_origin_set=bool(d.get("motor_origin_set",False))
            self.mcu_uptime["pc"]=float(d.get("uptime_ms",0))/1000.0;self.mcu_uptime["light"]=float(d.get("light",{}).get("uptime_ms",0))/1000.0
            for k in ("motor","light"):
                x=d.get(k,{});self.links[k].update(online=x.get("online",False),unstable=x.get("unstable",False));remote=x.get("last_ack_ms",0)
                if remote and remote!=self.links[k]["remote_ack"]:self.links[k]["remote_ack"]=remote;self.links[k]["last"]=time.monotonic()
            a=d.get("actual",{});m=a.get("motor",{});l=a.get("light",{});self.actual["angle"]=m.get("angle",self.actual["angle"]);self.actual["speed"]=m.get("speed",self.actual["speed"]);self.motor_motion=m.get("motion",self.motor_motion);self.motor_target_angle=float(m.get("target_angle",self.motor_target_angle));self.actual["first"]=bool(l.get("first",self.actual["first"]));self.actual["stars"]=bool(l.get("stars",self.actual["stars"]));mask=l.get("patterns",0)
            for i in range(1,9):self.actual[f"p{i}"]=bool(mask&(1<<(i-1)))
        elif t=="bad_line":self.log("UART受信失敗（不正なデータ）: "+d.get("line",""))
        elif t=="serial_error":self.log("UART受信失敗: "+d.get("error",""));self.ser=None;self.uart_health="failed"
    def position(self):
        if self.playing:return min(self.duration,self.seek_base+(time.monotonic()-self.play_origin)*self.rate)
        return self.seek_base
    def toggle_play(self):
        if not self.audio:return messagebox.showwarning("音声未選択","音声ファイルを選択してください")
        if self.playing:self.pause()
        else:self.play()
    def restart_from_beginning(self):
        if not self.audio:return messagebox.showwarning("音声未選択","音声ファイルを選択してください")
        if not messagebox.askyesno("最初から再生","再生位置を0秒へ戻して、最初から再生しますか？"):return
        if self.playing:self.pause()
        self.seek_base=0;self.pos.set(0);self.apply_timeline(0,force=True);self.play();self.log("音声を最初から再生")
    def play(self):
        try:
            playback_file=self.rate_audio_path();pygame.mixer.music.load(playback_file);pygame.mixer.music.play(start=self.seek_base/self.rate);self.play_origin=time.monotonic();self.playing=True;self.play_btn.config(text="Ⅱ  一時停止",bg=ORANGE)
        except Exception as e:messagebox.showerror("再生エラー",str(e))
    def pause(self):
        self.seek_base=self.position();pygame.mixer.music.stop();self.playing=False;self.play_btn.config(text="▶  再生",bg=GREEN)
    def seek(self,x):
        was=self.playing
        if was:self.pause()
        self.seek_base=max(0,min(self.duration,float(x)));self.pos.set(self.seek_base)
        if was:self.play()
        self.apply_timeline(self.seek_base,force=True)
    def seek_preview(self,v):
        if not self.playing:self.seek_base=float(v)
    def begin_scrub(self,_event=None):
        self.scrub_was_playing=self.playing
        if self.playing:self.pause()
    def end_scrub(self,_event=None):
        target=float(self.pos.get());resume=self.scrub_was_playing;self.scrub_was_playing=False;self.seek(target)
        if resume and self.audio:self.play()
    def jump_seconds(self):
        try:self.seek(float(self.jump_var.get()))
        except ValueError:messagebox.showerror("入力エラー","秒数を数値で入力してください")
    def jump_event(self,direction):
        if not self.timeline:return
        now=time.monotonic();p=self.position()
        if self.nav_step_index is not None and now-self.nav_step_at<1.5:index=self.nav_step_index
        else:
            index=-1
            for i,r in enumerate(self.timeline):
                if r["time"]<=p+.02:index=i
                else:break
        target=index+(-1 if direction<0 else 1);target=max(0,min(len(self.timeline)-1,target))
        if target!=index or direction<0:self.seek(self.timeline[target]["time"])
        self.nav_step_index=target;self.nav_step_at=time.monotonic()
    def choose_audio(self):
        p=filedialog.askopenfilename(filetypes=[("音声","*.mp3 *.wav *.ogg"),("すべて","*.*")]);
        if p:self.load_audio(p);self.save_cfg()
    def load_audio(self,p):
        if pygame is None:raise RuntimeError("pygameがありません")
        if not pygame.mixer.get_init():pygame.mixer.init()
        snd=pygame.mixer.Sound(p);self.duration=snd.get_length();self.audio=p;self.scale.config(to=max(1,self.duration));self.audio_label.config(text="音声: "+Path(p).name)
    def choose_timeline(self):
        p=filedialog.askopenfilename(filetypes=[("タイムラインTXT","*.txt"),("すべて","*.*")]);
        if p:
            try:self.load_timeline_file(p);self.save_cfg()
            except Exception as e:messagebox.showerror("読込エラー",str(e))
    def load_timeline_file(self,p):self.timeline=load_timeline(p);self.timeline_path=p;self.log(f"タイムライン読込: {p}");self.refresh_step_overview();self.apply_timeline(self.position(),True)
    def refresh_step_overview(self):
        if not hasattr(self,"step_tree"):return
        self.timeline_times=[r["time"] for r in self.timeline]
        self.clear_step_value_colors()
        self.step_tree.delete(*self.step_tree.get_children())
        for i,r in enumerate(self.timeline):self.step_tree.insert("","end",iid=f"step_{i}",values=[f"STEP{i+1}",f'{r["time"]:.1f}',f'{r["angle"]:.2f}',f'{r["speed"]:.2f}',*("" for _k in FIELDS[2:])])
        self.schedule_step_value_colors()
    def clear_step_value_colors(self):
        for label in self.step_value_labels:
            try:label.destroy()
            except tk.TclError:pass
        self.step_value_labels=[]
    def schedule_step_value_colors(self,delay=18):
        if self.step_color_job:
            try:self.root.after_cancel(self.step_color_job)
            except tk.TclError:pass
        self.step_color_job=self.root.after(delay,self.run_scheduled_step_colors)
    def run_scheduled_step_colors(self):self.step_color_job=None;self.refresh_step_value_colors()
    def refresh_step_value_colors(self):
        if not hasattr(self,"step_tree") or self.refreshing_step_colors:return
        self.refreshing_step_colors=True
        try:
            for label in self.step_value_labels:label.place_forget()
            self.step_tree.update_idletasks()
            used=0
            for i,r in enumerate(self.timeline):
                iid=f"step_{i}"
                if not self.step_tree.exists(iid):continue
                bg="#34475a" if i==self.current_step_shown else "#101821"
                for key in FIELDS[2:]:
                    b=self.step_tree.bbox(iid,key)
                    if not b:continue
                    x,y,w,h=b;on=bool(r[key])
                    if used>=len(self.step_value_labels):
                        label=tk.Label(self.step_tree,font=("Yu Gothic UI",9,"bold"));label.bind("<Double-1>",lambda _e,l=label:self.jump_to_step(l._step_index));label.bind("<MouseWheel>",self.on_step_mousewheel);self.step_value_labels.append(label)
                    else:label=self.step_value_labels[used]
                    used+=1;label._step_index=i
                    label.config(text="ON" if on else "OFF",bg=bg,fg=GREEN if on else RED);label.place(x=x+1,y=y+1,width=max(1,w-2),height=max(1,h-2))
        finally:self.refreshing_step_colors=False
    def scroll_step_x(self,*args):self.step_tree.xview(*args);self.schedule_step_value_colors()
    def scroll_step_y(self,*args):self.step_tree.yview(*args);self.schedule_step_value_colors()
    def on_step_mousewheel(self,event):
        self.step_tree.yview_scroll(-1 if event.delta>0 else 1,"units");self.schedule_step_value_colors();return "break"
    def toggle_step_jump(self):
        enabled=not self.step_jump_enabled.get();self.step_jump_enabled.set(enabled);self.step_jump_btn.config(text=f'ダブルクリック移動: {"ON" if enabled else "OFF"}',bg="#265f43" if enabled else "#3d4652");self.log("STEPダブルクリック移動: "+("ON" if enabled else "OFF"))
    def on_step_double_click(self,event):
        if not self.step_jump_enabled.get():return
        iid=self.step_tree.identify_row(event.y)
        if not iid.startswith("step_"):return
        try:index=int(iid.split("_",1)[1])
        except ValueError:return
        self.jump_to_step(index)
    def jump_to_step(self,index):
        if not self.step_jump_enabled.get():return
        try:target=self.timeline[index]["time"]
        except IndexError:return
        self.seek(target);self.nav_step_index=index;self.nav_step_at=time.monotonic();self.log(f"STEP{index+1}へ移動 ({target:.3f}秒)")
    def update_step_highlight(self,p):
        if not hasattr(self,"step_tree"):return
        index=bisect.bisect_right(self.timeline_times,p+.001)-1;current=index if index>=0 else None
        if current==self.current_step_shown:return
        old=self.current_step_shown;self.current_step_shown=current
        if old is not None and self.step_tree.exists(f"step_{old}"):self.step_tree.item(f"step_{old}",tags=())
        if current is not None and self.step_tree.exists(f"step_{current}"):self.step_tree.item(f"step_{current}",tags=("current",));self.step_tree.see(f"step_{current}")
        self.schedule_step_value_colors()
    def apply_timeline(self,p,force=False):
        if not self.timeline or not self.auto.get():return
        rows=[r for r in self.timeline if r["time"]<=p+.001];r=rows[-1] if rows else self.timeline[0];new={k:r[k] for k in FIELDS}
        if force or new!=self.desired:self.desired=new;self.send(fade=self.playing and not force)
    def next_info(self,p):
        future=[r for r in self.timeline if r["time"]>p+.01]
        if not future:return "次の変更: なし"
        n=future[0];cur=self.desired;diff=[]
        for k in FIELDS:
            if n[k]!=cur.get(k):diff.append(f'{LABELS[k]}→{n[k] if k in ("angle","speed") else ("ON" if n[k] else "OFF")}')
        return f'次の変更まで {n["time"]-p:.1f}秒 ({fmt_time(n["time"])})\n' + (" / ".join(diff) or "値の差分なし")
    def on_override(self):self.send(True);self.update_values()
    def manual_changed(self):self.send(True)
    def toggle_manual(self,k):self.manual[k].set("OFF" if as_bool(self.manual[k].get()) else "ON");self.send(True)
    def auto_changed(self):
        if not self.auto.get() and not messagebox.askyesno("自動変更をOFF","音声に同期した設定値の自動変更を停止しますか？"):
            self.auto.set(True);return
        self.log("設定値自動変更: "+("ON" if self.auto.get() else "OFF"));self.apply_timeline(self.position(),True)
    def change_rate(self,_=None):
        new=float(self.rate_var.get().rstrip("x"));p=self.position();was=self.playing
        if self.rate_conversion_active:
            self.rate_var.set(f"{self.rate:g}x");return
        if was:self.pause()
        self.seek_base=p
        if not self.audio or abs(new-1.0)<.0001:
            self.rate=new
            if was:self.play()
            return
        self.rate_conversion_active=True;self.play_btn.configure(state="disabled",text="音声を変換中...")
        threading.Thread(target=self.prepare_rate_audio_worker,args=(new,p,was),daemon=True).start()
        return
        new=float(self.rate_var.get().rstrip("x"));p=self.position();was=self.playing
        if was:self.pause()
        self.rate=new;self.seek_base=p
        try:
            if self.audio:self.rate_audio_path()
            if was:self.play()
            self.log(f"再生速度 {new}x（音声とタイムラインの両方へ反映）")
        except Exception as e:
            self.rate=1.0;self.rate_var.set("1.0x");self.seek_base=p
            messagebox.showerror("倍速音声の作成エラー",str(e))
            if was:self.play()
    def prepare_rate_audio_worker(self,new,position,was_playing):
        try:self.rate_results.put((True,new,position,was_playing,self.build_rate_audio(new),""))
        except Exception as e:self.rate_results.put((False,new,position,was_playing,"",str(e)))
    def finish_rate_change(self,result):
        ok,new,position,was_playing,_path,error=result;self.rate_conversion_active=False;self.play_btn.configure(state="normal")
        if ok:
            self.rate=new;self.seek_base=position;self.log(f"再生速度 {new}x（ピッチ維持）")
            if was_playing:self.play()
            else:self.play_btn.config(text="▶  再生",bg=GREEN)
        else:
            self.rate_var.set(f"{self.rate:g}x");self.seek_base=position;self.play_btn.config(text="▶  再生",bg=GREEN);messagebox.showerror("倍速音声の作成エラー",error)
    def build_rate_audio(self,rate):
        source=Path(self.audio);cache_dir=APP_DIR/"audio_rate_cache";cache_dir.mkdir(parents=True,exist_ok=True);stat=source.stat();key=hashlib.sha1(f"pitch-v3|{source.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{rate:.3f}".encode("utf-8")).hexdigest()[:16];target=cache_dir/f"{key}_{rate:g}x_pitch.wav"
        if target.exists() and target.stat().st_size>44:return str(target)
        if source.suffix.lower()!=".wav":raise ValueError("ピッチを維持した倍速再生はWAV音声を選択してください。")
        work=target.with_suffix(".parts");work.mkdir(parents=True,exist_ok=True);temporary=target.with_suffix(".tmp.wav")
        try:
            with wave.open(str(source),"rb") as src:
                params=src.getparams();chunk_frames=params.framerate*30
                with wave.open(str(temporary),"wb") as dst:
                    dst.setnchannels(params.nchannels);dst.setsampwidth(params.sampwidth);dst.setframerate(params.framerate);part=0
                    while True:
                        raw=src.readframes(chunk_frames)
                        if not raw:break
                        frames=len(raw)//(params.nchannels*params.sampwidth);part_in=work/f"in_{part}.wav";part_out=work/f"out_{part}.wav"
                        with wave.open(str(part_in),"wb") as piece:piece.setparams(params);piece.writeframes(raw)
                        stretch_audio(str(part_in),str(part_out),ratio=1.0/rate);expected=round(frames/rate)
                        with wave.open(str(part_out),"rb") as stretched:
                            data=stretched.readframes(expected);actual=len(data)//(params.nchannels*params.sampwidth);dst.writeframesraw(data)
                            if actual<expected:dst.writeframesraw(b"\x00"*((expected-actual)*params.nchannels*params.sampwidth))
                        part_in.unlink(missing_ok=True);part_out.unlink(missing_ok=True);part+=1
            os.replace(temporary,target);return str(target)
        finally:
            temporary.unlink(missing_ok=True)
            try:work.rmdir()
            except OSError:pass
    def rate_audio_path(self):
        if not self.audio or abs(self.rate-1.0)<.0001:return self.audio
        return self.build_rate_audio(self.rate)
        source=Path(self.audio);cache_dir=APP_DIR/"audio_rate_cache";cache_dir.mkdir(parents=True,exist_ok=True)
        stat=source.stat();key=hashlib.sha1(f"pitch-v2|{source.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{self.rate:.3f}".encode("utf-8")).hexdigest()[:16];target=cache_dir/f"{key}_{self.rate:g}x_pitch.wav"
        if target.exists() and target.stat().st_size>44:return str(target)
        self.root.config(cursor="wait");self.root.update_idletasks()
        try:
            stretch_source=source
            if source.suffix.lower()!=".wav":
                decoded=cache_dir/f"{key}_decoded.wav";sound=pygame.mixer.Sound(str(source));frequency,fmt,channels=pygame.mixer.get_init();width=abs(fmt)//8
                with wave.open(str(decoded),"wb") as dst:dst.setnchannels(channels);dst.setsampwidth(width);dst.setframerate(frequency);dst.writeframes(sound.get_raw())
                stretch_source=decoded
            stretch_audio(str(stretch_source),str(target),ratio=1.0/self.rate)
            self.fix_stretched_duration(stretch_source,target)
            return str(target)
        except Exception:
            try:target.unlink(missing_ok=True)
            except Exception:pass
            raise
        finally:self.root.config(cursor="")
    def fix_stretched_duration(self,source,target):
        with wave.open(str(source),"rb") as src:expected=round(src.getnframes()/self.rate)
        with wave.open(str(target),"rb") as stretched:
            params=stretched.getparams();actual=stretched.getnframes()
            if actual==expected:return
            corrected=target.with_suffix(".corrected.wav")
            with wave.open(str(corrected),"wb") as dst:
                dst.setnchannels(params.nchannels);dst.setsampwidth(params.sampwidth);dst.setframerate(params.framerate);remaining=expected
                while remaining>0:
                    data=stretched.readframes(min(remaining,65536))
                    if not data:break
                    frames=len(data)//(params.nchannels*params.sampwidth);dst.writeframesraw(data);remaining-=frames
                if remaining>0:dst.writeframesraw(b"\x00"*(remaining*params.nchannels*params.sampwidth))
        os.replace(corrected,target)
    def check_output_device(self):
        detected=default_output_name()
        if not detected or detected==self.output_device:return
        old=self.output_device;position=self.position();was_playing=self.playing
        try:
            if pygame.mixer.get_init():pygame.mixer.music.stop();pygame.mixer.quit()
            pygame.mixer.init();self.output_device=default_output_name();self.speaker_label.config(text="出力スピーカー: "+self.output_device)
            if was_playing and self.audio:self.seek_base=position;self.play()
            self.log(f"音声出力を切替: {old} → {self.output_device}")
        except Exception as e:self.output_device=detected;self.speaker_label.config(text="出力スピーカー: "+detected+"（切替失敗）");self.log(f"音声出力切替失敗: {e}")
    def actual_link_ok(self,device):
        pc_ok=bool(self.ser and self.last_pc and time.monotonic()-self.last_pc<3)
        if device=="motor":return pc_ok
        link=self.links[device];last=link["last"]
        return bool(pc_ok and link["online"] and not link["unstable"] and last and time.monotonic()-last<max(3,self.cfg["esp_interval"]+2))
    def update_values(self):
        try:d=self.effective()
        except:d=self.desired
        for k,w in self.vars.items():
            a=d[k];b=self.actual[k];link_ok=self.actual_link_ok("motor" if k in ("angle","speed") else "light");link_ok=link_ok and (self.motor_origin_set if k in ("angle","speed") else True);continuous=k=="angle" and abs(abs(a)-999.0)<.01
            continuous_text="連続回転 (CW)" if a>0 else "連続回転 (CCW)"
            w["req"].set(continuous_text if continuous else (f"{a:.2f}" if k in ("angle","speed") else ("ON" if a else "OFF")))
            if k=="angle":actual_text=f"現在角度 {b%360.0:.2f}°"
            elif k=="speed":actual_text=f"{b:.2f} °/s"
            else:actual_text="ON" if b else "OFF"
            w["act"].set(actual_text if link_ok else actual_text+"?");value_ok=True if continuous else (abs(a-b)<.01 if k in ("angle","speed") else a==b);ok=value_ok and link_ok
            row_bg="#30343b" if self.override[k].get() else ("#54202a" if not ok else CARD);w["box"].config(bg=row_bg)
            for name in ("name","req_label","act_label"):w[name].config(bg=row_bg)
            w["check"].config(bg=row_bg,activebackground=row_bg);w["led"].config(bg=row_bg);w["led"].set(GREEN if ok else (RED if self.flash else OFF))
            if k not in ("angle","speed"):
                w["req_label"].config(fg=GREEN if a else RED);w["act_label"].config(fg=(GREEN if b else RED) if link_ok else ORANGE)
                manual_on=as_bool(self.manual[k].get());w["control"].config(fg=GREEN if manual_on else RED,activeforeground=GREEN if manual_on else RED)
            else:w["req_label"].config(fg=TEXT);w["act_label"].config(fg=TEXT if link_ok else ORANGE)
        if self.motor_origin_set:self.origin_status.config(text="原点設定済み：モーター制御可能",bg="#1f513b",fg="#9ff2be")
        else:self.origin_status.config(text="原点未設定：モーター移動禁止",bg="#54202a",fg="#ffb6bd")
    def update_status(self):
        now=time.monotonic();pc_ok=self.ser is not None and self.last_pc and now-self.last_pc<3
        if self.ser:
            if self.uart_health=="waiting" and self.uart_connected_at and now-self.uart_connected_at<3:new_uart="waiting"
            else:new_uart="ok" if pc_ok else "failed"
            if new_uart!=self.uart_health:
                if new_uart=="failed":self.log("UART通信失敗: 統括マイコンから3秒以上応答がありません")
                elif new_uart=="ok":self.log("UART通信確立" if self.uart_health=="waiting" else "UART通信復帰")
                self.uart_health=new_uart
        elif self.uart_health not in ("failed","disconnected"):self.uart_health="disconnected"
        for k in ("pc","light"):
            card,led,title,age=self.status_widgets[k]
            if k=="pc":last=self.last_pc;online=pc_ok;unstable=False
            else:last=self.links[k]["last"];online=self.links[k]["online"] and last and now-last<max(3,self.cfg["esp_interval"]+2);unstable=self.links[k]["unstable"]
            card_bg="#47262b" if not online else CARD
            card.config(bg=card_bg);led.config(bg=card_bg);title.config(bg=card_bg);age.config(bg=card_bg)
            if online and not unstable:led.set(GREEN)
            else:led.set((ORANGE if unstable else RED) if self.flash else OFF)
            communication="最終通信: --" if not last else f"最終通信から {now-last:.1f}秒";uptime=self.mcu_uptime[k];age.config(text=f"{communication}　　起動後 {fmt_uptime(uptime)}" if uptime else f"{communication}　　起動後 --")
    def tick(self):
        while not self.rx.empty():self.process(self.rx.get())
        while not self.rate_results.empty():self.finish_rate_change(self.rate_results.get())
        p=self.position()
        now=time.monotonic()
        if now-self.last_speaker_check>=2:self.last_speaker_check=now;self.check_output_device()
        if self.playing and p>=self.duration:self.pause();self.seek_base=self.duration
        if self.auto.get():self.apply_timeline(p)
        self.pos.set(p);self.time_label.config(text=f"{fmt_time(p)} / {fmt_time(self.duration)}");remain=max(0,(self.duration-p)/self.rate);self.end_label.config(text=f"残り {fmt_time(remain)} / 予定 {(datetime.now()+timedelta(seconds=remain)):%H:%M:%S}");self.next_label.config(text=self.next_info(p));self.update_step_highlight(p)
        if now-self.last_flash_at>=.5:self.flash=not self.flash;self.last_flash_at=now
        self.update_values();self.update_status()
        if self.ser and now-self.last_keepalive>=1.0:self.write({"cmd":"ping"});self.last_keepalive=now
        if self.ser and (self.last_sent is None or time.monotonic()-getattr(self,"last_uart",0)>=self.cfg["uart_interval"]):self.send(True);self.last_uart=time.monotonic()
        self.root.after(100,self.tick)
    def settings_dialog(self):
        w=tk.Toplevel(self.root);w.title("通信設定");w.configure(bg=PANEL);vals={}
        specs=(("uart_interval","PC→統括 定期送信間隔 (秒)"),("esp_interval","統括→子機 定期送信間隔 (秒)"),("retry_timeout","ACK待機 (秒)"),("max_retries","最大再送回数"))
        for i,(k,l) in enumerate(specs):self.label(w,l).grid(row=i,column=0,sticky="w",padx=12,pady=8);v=tk.StringVar(value=str(self.cfg[k]));tk.Entry(w,textvariable=v).grid(row=i,column=1,padx=12);vals[k]=v
        def ok():
            try:
                for k in vals:self.cfg[k]=int(vals[k].get()) if k=="max_retries" else float(vals[k].get())
                self.configure_mcu();self.save_cfg();w.destroy();self.log("通信設定を更新")
            except ValueError:messagebox.showerror("入力エラー","数値を入力してください",parent=w)
        self.button(w,"保存",ok,bg=BLUE).grid(row=len(specs),column=0,columnspan=2,pady=12)
    def send_motor_calibration(self,action,speed=0.0,value=0.0):
        if not self.ser or not getattr(self.ser,"is_open",False):self.log("モーター校正送信失敗: UART未接続");messagebox.showerror("UART未接続","統括マイコンへUART接続してから操作してください");return False
        ok=self.write({"cmd":"motor_cal","action":action,"speed":float(speed),"value":float(value)})
        if ok:self.log(f"モーター校正送信 action={action} speed={float(speed):.3f} value={float(value):.3f}")
        return ok
    def open_motor_calibration(self):
        if self.emergency_stop:return messagebox.showwarning("緊急停止中","緊急停止を解除するまで、モーター0°位置設定は使用できません。",parent=self.root)
        if self.playing:return messagebox.showwarning("再生中は操作できません","音声を一時停止または停止してから、モーター0°位置設定を開いてください。",parent=self.root)
        if self.calibration_window and self.calibration_window.w.winfo_exists():self.calibration_window.w.lift();return
        self.calibration_window=MotorCalibrationWindow(self)
    def timeline_editor(self):TimelineEditor(self)
    def close(self):
        try:
            if self.playing:self.pause()
            if self.ser:self.ser.close()
            self.save_cfg()
        finally:self.root.destroy()

class MotorCalibrationWindow:
    def __init__(self,app):
        self.app=app;self.w=tk.Toplevel(app.root);self.w.title("モーター0°位置設定");self.w.geometry("650x570");self.w.resizable(False,False);self.w.configure(bg=BG);self.speed=tk.StringVar(value="0.0");self.delta=tk.StringVar(value="1.0");self.current_angle=tk.StringVar(value="0.0");self.jog_request_until=0;self.jog_requested=False;self.jog_requested_direction=0;self.build();self.w.protocol("WM_DELETE_WINDOW",self.finish);self.app.send_motor_calibration("stop");self.update_status()
    def build(self):
        self.app.label(self.w,"モーター0°位置設定",font=("Yu Gothic UI",18,"bold")).pack(anchor="w",padx=18,pady=(15,3));self.app.label(self.w,"校正コマンド送信後は通常の周期モーター指令を停止します。作業後は必ず「通常制御へ戻る」を押してください。",fg=ORANGE,wraplength=610,justify="left").pack(anchor="w",padx=18,pady=(0,10));self.status=self.app.label(self.w,"状態確認中…",bg=CARD,fg="#9ec7ef",anchor="w",justify="left");self.status.pack(fill="x",padx=18,pady=5,ipadx=10,ipady=7)
        jog=self.app.frame(self.w,bg=CARD);jog.pack(fill="x",padx=18,pady=6);self.app.label(jog,"連続回転（ジョグ）",bg=CARD,font=("Yu Gothic UI",11,"bold")).grid(row=0,column=0,columnspan=6,sticky="w",padx=10,pady=(8,4));self.motion=self.app.label(jog,"● 停止中",bg="#26313d",fg="#b8c5d3",font=("Yu Gothic UI",11,"bold"));self.motion.grid(row=0,column=3,columnspan=2,padx=8,pady=(6,2),ipadx=10,ipady=3);self.app.label(jog,"回転速度 (°/s)",bg=CARD).grid(row=1,column=0,padx=10,pady=8);tk.Entry(jog,textvariable=self.speed,width=10,bg="#0e151e",fg=TEXT,insertbackground=TEXT,relief="flat").grid(row=1,column=1,padx=4);self.jog_btn=self.app.button(jog,"▶ 回転",self.toggle_jog,bg=GREEN);self.jog_btn.grid(row=1,column=2,padx=8);self.app.label(jog,"正: 時計回り　／　負: 反時計回り",bg=CARD,fg="#9ec7ef",font=("Yu Gothic UI",9)).grid(row=2,column=0,columnspan=5,sticky="w",padx=10,pady=(0,8))
        rel=self.app.frame(self.w,bg=CARD);rel.pack(fill="x",padx=18,pady=6);self.app.label(rel,"相対角度移動",bg=CARD,font=("Yu Gothic UI",11,"bold")).grid(row=0,column=0,columnspan=5,sticky="w",padx=10,pady=(8,4));self.app.label(rel,"移動角度 (°)",bg=CARD).grid(row=1,column=0,padx=10,pady=8);tk.Entry(rel,textvariable=self.delta,width=10,bg="#0e151e",fg=TEXT,insertbackground=TEXT,relief="flat").grid(row=1,column=1,padx=4);self.app.button(rel,"－角度移動",lambda:self.move_relative(-1)).grid(row=1,column=2,padx=6);self.app.button(rel,"＋角度移動",lambda:self.move_relative(1)).grid(row=1,column=3,padx=6)
        origin=self.app.frame(self.w,bg=CARD);origin.pack(fill="x",padx=18,pady=6);self.app.label(origin,"論理角度の再設定",bg=CARD,font=("Yu Gothic UI",11,"bold")).grid(row=0,column=0,columnspan=5,sticky="w",padx=10,pady=(8,4));self.app.button(origin,"現在位置を0°に設定",self.set_zero,bg=RED).grid(row=1,column=0,padx=10,pady=8);self.app.label(origin,"現在位置を",bg=CARD).grid(row=1,column=1,padx=(15,3));tk.Entry(origin,textvariable=self.current_angle,width=10,bg="#0e151e",fg=TEXT,insertbackground=TEXT,relief="flat").grid(row=1,column=2,padx=3);self.app.label(origin,"°として設定",bg=CARD).grid(row=1,column=3,padx=3);self.app.button(origin,"角度設定",self.set_angle,bg=ORANGE).grid(row=1,column=4,padx=8)
        self.app.button(self.w,"通常制御へ戻る（校正終了）",self.finish,bg=GREEN).pack(pady=14,ipadx=25,ipady=5)
    def numbers(self):
        try:
            speed=float(self.speed.get());delta=abs(float(self.delta.get()));angle=float(self.current_angle.get())
            if speed==0:raise ValueError("回転速度は0以外にしてください")
            return speed,delta,angle
        except ValueError as e:messagebox.showerror("入力エラー",str(e),parent=self.w);return None
    def command(self,action,speed=0,value=0):self.app.send_motor_calibration(action,speed,value)
    def toggle_jog(self):
        running=abs(self.app.actual["speed"])>.001 or (self.jog_requested and time.monotonic()<self.jog_request_until)
        if running:
            self.command("stop");self.jog_requested=False;self.jog_requested_direction=0;self.jog_request_until=time.monotonic()+1.0;self.jog_btn.config(text="▶ 回転",bg=GREEN)
        else:
            n=self.numbers()
            if n:
                speed=n[0];self.command("jog_cw" if speed>0 else "jog_ccw",abs(speed),0);self.jog_requested=True;self.jog_requested_direction=1 if speed>0 else -1;self.jog_request_until=time.monotonic()+1.0;self.jog_btn.config(text="■ 停止",bg=RED)
    def move_relative(self,direction):
        n=self.numbers()
        if n:self.jog_requested=False;self.jog_requested_direction=0;self.command("move_relative",abs(n[0]),direction*n[1])
    def set_zero(self):
        if messagebox.askyesno("0°位置を設定","現在のモーター位置を0°として記憶しますか？",parent=self.w):self.command("set_zero")
    def set_angle(self):
        try:angle=float(self.current_angle.get())%360.0
        except ValueError:messagebox.showerror("入力エラー","現在角度を数値で入力してください",parent=self.w);return
        if messagebox.askyesno("現在角度を設定",f"現在のモーター位置を {angle:.3f}° として記憶しますか？",parent=self.w):self.command("set_angle",0,angle)
    def update_status(self):
        if not self.w.winfo_exists():return
        known=self.app.actual_link_ok("motor");suffix="" if known else "?";mode="校正モード" if self.app.motor_calibration_mode else "通常制御（校正コマンド待機）";origin="設定済み" if self.app.motor_origin_set else "未設定（通常移動は禁止）";speed=self.app.actual['speed'];motion=self.app.motor_motion
        if motion in ("jog_cw","jog_ccw") or (self.jog_requested and time.monotonic()<self.jog_request_until):
            direction="反時計回り" if motion=="jog_ccw" or (motion not in ("jog_cw","jog_ccw") and self.jog_requested_direction<0) else "時計回り";self.jog_requested=True;self.motion.config(text=f"● 連続回転中：{direction}",bg="#594219",fg="#ffd27a");self.jog_btn.config(text="■ 停止",bg=RED,state="normal")
        elif motion=="relative":
            self.jog_requested=False;self.motion.config(text=f"◆ 相対角度移動中　目標 {self.app.motor_target_angle:.3f}°\n連続回転ではありません",bg="#173e5a",fg="#8fd3ff",justify="center");self.jog_btn.config(text="▶ 回転",bg=GREEN,state="disabled")
        elif time.monotonic()>=self.jog_request_until:self.jog_requested=False;self.jog_requested_direction=0;self.motion.config(text="● 停止中（連続回転なし）",bg="#26313d",fg="#b8c5d3");self.jog_btn.config(text="▶ 回転",bg=GREEN,state="normal")
        self.status.config(text=f"統括状態: {mode}　原点: {origin}\n最終受信角度: {self.app.actual['angle']:.3f}°{suffix}　速度: {speed:.3f}°/s{suffix}");self.w.after(250,self.update_status)
    def finish(self):
        if not messagebox.askyesno("校正を終了","モーターを停止して通常のタイムライン制御へ戻りますか？",parent=self.w):return
        ok=self.app.send_motor_calibration("exit")
        if not ok and not messagebox.askyesno("送信失敗","終了指令を送信できませんでした。統括マイコンが校正モードのまま残る可能性があります。ウィンドウだけ閉じますか？",parent=self.w):return
        self.app.calibration_window=None;self.w.destroy()

class TimelineEditor:
    def __init__(self,app):
        self.app=app;self.w=tk.Toplevel(app.root);self.w.title("指示送信設定エディター");self.w.geometry("1380x650");self.w.configure(bg=BG);self.rows=[dict(r) for r in app.timeline];self.path=getattr(app,"timeline_path","");self.active_col="time";self.active_row=None;self.editor=None;self.cell_focus=None;self.value_labels=[];self.selected_color_label=None;self.refreshing_value_colors=False;self.value_color_job=None;self.drag_from=None;self.drag_to=None;self.drag_moved=False;self.copied_row=None;self.build();self.refresh()
    def build(self):
        bar=tk.Frame(self.w,bg=PANEL);bar.pack(fill="x",padx=10,pady=10)
        for text,cmd in (("選択行を引き継いで追加",self.add),("行を複製",self.duplicate),("行を削除",self.delete),("TXTインポート",self.import_),("上書き保存",self.save),("名前を付けて保存",self.save_as),("メインへ反映",self.apply)):
            self.app.button(bar,text,cmd).pack(side="left",padx=3)
        self.app.button(bar,"使い方",self.show_help,bg=HELP_BLUE).pack(side="left",padx=3)
        self.cols=("step","time")+tuple(FIELDS);self.tree=ttk.Treeview(self.w,columns=self.cols,show="headings",selectmode="browse",style="Dark.Treeview")
        for c in self.cols:
            title="STEP" if c=="step" else "時刻(s)" if c=="time" else LABELS[c];self.tree.heading(c,text=title);self.tree.column(c,width=75 if c=="step" else 100,anchor="center",stretch=True)
        self.tree.pack(fill="both",expand=True,padx=10);self.tree.bind("<Double-1>",self.begin_cell_edit);self.tree.bind("<ButtonPress-1>",self.start_row_drag);self.tree.bind("<B1-Motion>",self.drag_row_motion);self.tree.bind("<ButtonRelease-1>",self.finish_row_drag);self.tree.bind("<Control-c>",self.copy_cell);self.tree.bind("<Control-C>",self.copy_cell);self.tree.bind("<Control-v>",self.paste_cell);self.tree.bind("<Control-V>",self.paste_cell);self.tree.bind("<MouseWheel>",lambda _e:self.schedule_value_colors(),add="+");self.tree.bind("<Configure>",lambda _e:self.schedule_value_colors(),add="+")
        self.app.label(self.w,"セルをダブルクリックして直接編集　｜　Ctrl+C / Ctrl+V でセル値をコピー　｜　STEP列では行の複製、ドラッグで順番変更　｜　999＝時計回り／-999＝反時計回り無限回転",fg=MUTED).pack(anchor="w",padx=14,pady=10)
    def show_help(self):
        self.app.show_help_window("指示送信設定の使い方","""【セル編集】
時刻・角度・速度はセルをダブルクリックして入力し、Enterで確定します。ON/OFFセルはダブルクリックするたびに切り替わります。

【コピー・貼り付け】
セルをクリックしてCtrl+C、貼り付け先をクリックしてCtrl+Vを押します。ON/OFFもコピーできます。STEP列を選んでコピー・貼り付けすると行全体を複製します。

【行操作】
STEP列をクリックすると行全体を選択します。「選択行を引き継いで追加」は、その行と同じ内容を直後へ追加します。STEP列を上下へドラッグすると順番を変更できます。

【角度】
通常角度は0°以上360°未満です。999を指定すると時計回り、-999を指定すると反時計回り無限回転になります。

【保存と反映】
上書き保存または名前を付けて保存でTXTへ保存します。「メインへ反映」で現在の編集内容をメイン画面のタイムラインへ適用します。""",self.w)
    def refresh(self):
        self.clear_cell_focus();self.clear_value_colors()
        self.tree.delete(*self.tree.get_children())
        for i,r in enumerate(self.rows):self.tree.insert("", "end",iid=str(i),values=[f"STEP{i+1}",f'{r["time"]:.3f}',f'{r["angle"]:.2f}',f'{r["speed"]:.2f}',*("ON" if r[k] else "OFF" for k in FIELDS[2:])])
        self.schedule_value_colors()
    def schedule_value_colors(self):
        if self.value_color_job:
            try:self.w.after_cancel(self.value_color_job)
            except tk.TclError:pass
        self.value_color_job=self.w.after(15,self.refresh_value_colors)
    def selected(self):
        s=self.tree.selection();return int(s[0]) if s else None
    def column_at(self,event):
        n=int(self.tree.identify_column(event.x).lstrip("#") or 0);return self.cols[n-1] if 0<n<=len(self.cols) else None
    def remember_cell(self,event):
        c=self.column_at(event);row_id=self.tree.identify_row(event.y)
        if not c or not row_id:return
        self.select_cell(int(row_id),c)
    def start_row_drag(self,event):
        self.drag_from=None;self.drag_to=None;self.drag_moved=False
        if self.column_at(event)!="step":return
        row_id=self.tree.identify_row(event.y)
        if not row_id:return
        self.drag_from=int(row_id);self.drag_to=self.drag_from;self.select_cell(self.drag_from,"step")
    def drag_row_motion(self,event):
        if self.drag_from is None:return
        row_id=self.tree.identify_row(event.y)
        if not row_id:return "break"
        target=int(row_id);self.drag_moved=self.drag_moved or target!=self.drag_from;self.drag_to=target
        self.tree.selection_set(row_id);self.tree.focus(row_id);self.tree.see(row_id)
        return "break"
    def finish_row_drag(self,event):
        if self.drag_from is None:
            self.remember_cell(event);return
        src=self.drag_from;dest=self.drag_to;was_moved=self.drag_moved
        self.drag_from=None;self.drag_to=None;self.drag_moved=False
        if was_moved and dest is not None and src!=dest:self.move_row(src,dest)
        else:self.select_cell(src,"step")
        return "break"
    def move_row(self,src,dest):
        if not (0<=src<len(self.rows)):return
        item=self.rows.pop(src);dest=max(0,min(dest,len(self.rows)));self.rows.insert(dest,item)
        self.refresh();self.active_row=dest;self.active_col="step";self.tree.selection_set(str(dest));self.tree.focus(str(dest));self.tree.see(str(dest));self.schedule_value_colors()
    def select_cell(self,row,key):
        self.active_col=key;self.active_row=row
        if key=="step":
            self.clear_cell_focus();self.tree.selection_set(str(row));self.tree.focus(str(row));self.w.after_idle(self.restyle_value_colors)
        else:
            self.tree.selection_remove(self.tree.selection());self.show_cell_focus(row,key);self.tree.focus_set();self.restyle_value_colors()
    def select_colored_cell(self,label,row,key):
        self.active_col=key;self.active_row=row;self.clear_cell_focus();self.tree.selection_remove(self.tree.selection())
        self.restyle_value_colors();label.focus_set()
    def restyle_value_colors(self):
        selected=set(self.tree.selection());self.selected_color_label=None
        for label in self.value_labels:
            try:
                on=bool(self.rows[label._row][label._key]);active=label._row==self.active_row and label._key==self.active_col;row_selected=str(label._row) in selected;label.config(bg="#0875c1" if active or row_selected else "#101821",fg="#ffffff" if active or row_selected else (GREEN if on else RED),text="ON" if on else "OFF")
                if active and not row_selected:self.selected_color_label=label
            except (tk.TclError,IndexError):pass
    def clear_value_colors(self):
        for label in self.value_labels:
            try:label.destroy()
            except tk.TclError:pass
        self.value_labels=[];self.selected_color_label=None
    def refresh_value_colors(self):
        self.value_color_job=None
        if self.refreshing_value_colors:return
        self.refreshing_value_colors=True
        try:
            self.clear_value_colors();self.tree.update_idletasks();selected=set(self.tree.selection())
            for row,r in enumerate(self.rows):
                iid=str(row);bg="#0875c1" if iid in selected else "#101821"
                for key in FIELDS[2:]:
                    b=self.tree.bbox(iid,key)
                    if not b:continue
                    x,y,w,h=b;on=bool(r[key]);label=tk.Label(self.tree,text="ON" if on else "OFF",bg=bg,fg=GREEN if on else RED,font=("Yu Gothic UI",9,"bold"));label._row=row;label._key=key
                    label.place(x=x+1,y=y+1,width=max(1,w-2),height=max(1,h-2));label.bind("<Button-1>",lambda _e,l=label,rr=row,k=key:self.select_colored_cell(l,rr,k));label.bind("<Double-1>",lambda _e,rr=row,k=key:self.toggle_bool_cell(rr,k));label.bind("<Control-c>",self.copy_cell);label.bind("<Control-C>",self.copy_cell);label.bind("<Control-v>",self.paste_cell);label.bind("<Control-V>",self.paste_cell);label.bind("<MouseWheel>",self.on_value_mousewheel);self.value_labels.append(label)
                    if row==self.active_row and key==self.active_col and not selected:label.config(bg="#0875c1",fg="#ffffff");self.selected_color_label=label
        finally:self.refreshing_value_colors=False
    def on_value_mousewheel(self,event):
        self.tree.yview_scroll(-1 if event.delta>0 else 1,"units");self.schedule_value_colors();return "break"
    def clear_cell_focus(self):
        if self.cell_focus:self.cell_focus.destroy();self.cell_focus=None
    def show_cell_focus(self,row,key):
        self.clear_cell_focus();self.tree.update_idletasks();b=self.tree.bbox(str(row),key)
        if not b:return
        x,y,w,h=b;value=self.tree.set(str(row),key);border=tk.Frame(self.tree,bg="#0875c1");label=tk.Label(border,text=value,bg="#0875c1",fg="#ffffff",font=("Yu Gothic UI",9));label.pack(fill="both",expand=True,padx=1,pady=1)
        for widget in (border,label):widget.bind("<Double-1>",lambda _e,r=row,k=key:self.begin_edit_at(r,k));widget.bind("<Control-c>",self.copy_cell);widget.bind("<Control-C>",self.copy_cell);widget.bind("<Control-v>",self.paste_cell);widget.bind("<Control-V>",self.paste_cell)
        border.place(x=x,y=y,width=w,height=h);self.cell_focus=border
    def set_cell(self,row,key,value):
        try:
            if key in ("time","angle","speed"):self.rows[row][key]=float(value)
            elif key in FIELDS[2:]:
                v=str(value).strip().upper()
                if v not in ("ON","OFF","TRUE","FALSE","1","0"):raise ValueError("ONまたはOFFを入力してください")
                self.rows[row][key]=as_bool(v)
            self.active_row=row;self.active_col=key;self.refresh()
            if key not in FIELDS[2:]:self.show_cell_focus(row,key)
        except ValueError as e:messagebox.showerror("入力エラー",str(e),parent=self.w)
    def begin_cell_edit(self,event):
        row_id=self.tree.identify_row(event.y);key=self.column_at(event)
        if not row_id or not key or key=="step":return
        if key in FIELDS[2:]:self.toggle_bool_cell(int(row_id),key)
        else:self.begin_edit_at(int(row_id),key)
    def toggle_bool_cell(self,row,key):
        self.rows[row][key]=not bool(self.rows[row][key]);self.active_row=row;self.active_col=key;self.tree.set(str(row),key,"ON" if self.rows[row][key] else "OFF");self.restyle_value_colors();return "break"
    def begin_edit_at(self,row,key):
        row_id=str(row);self.active_col=key;self.active_row=row;self.clear_cell_focus();self.tree.selection_remove(self.tree.selection());b=self.tree.bbox(row_id,key)
        if not b:return
        if self.editor:self.editor.destroy()
        x,y,w,h=b;current=self.tree.set(row_id,key)
        if key in FIELDS[2:]:return self.toggle_bool_cell(row,key)
        else:
            e=tk.Entry(self.tree,bg="#eef3f8",fg="#111820",insertbackground="#111820",relief="solid");e.insert(0,current);e.select_range(0,"end");e.bind("<Return>",lambda _e:self.finish_edit(row,key,e.get()));e.bind("<FocusOut>",lambda _e:self.finish_edit(row,key,e.get()));e.bind("<Escape>",lambda _e:e.destroy())
        self.editor=e;e.place(x=x,y=y,width=w,height=h);e.focus_set()
    def finish_edit(self,row,key,value):
        if self.editor:self.editor.destroy();self.editor=None
        self.set_cell(row,key,value)
    def copy_cell(self,_event=None):
        i=self.active_row
        if i is None:return "break"
        if self.active_col=="step":
            self.copied_row=dict(self.rows[i]);value="PLANE_STEP_ROW\t"+json.dumps(self.copied_row,ensure_ascii=False);self.w.clipboard_clear();self.w.clipboard_append(value);return "break"
        value=self.tree.set(str(i),self.active_col);self.w.clipboard_clear();self.w.clipboard_append(value);return "break"
    def paste_cell(self,_event=None):
        i=self.active_row
        if i is None:return "break"
        if self.active_col=="step":
            row=None
            try:
                value=self.w.clipboard_get()
                if value.startswith("PLANE_STEP_ROW\t"):row=json.loads(value.split("\t",1)[1])
            except (tk.TclError,json.JSONDecodeError):pass
            if row is None and self.copied_row is not None:row=dict(self.copied_row)
            if row is not None:
                self.rows.insert(i+1,dict(row));new=i+1;self.refresh();self.active_row=new;self.active_col="step";self.tree.selection_set(str(new));self.tree.focus(str(new));self.tree.see(str(new));self.schedule_value_colors()
            return "break"
        try:self.set_cell(i,self.active_col,self.w.clipboard_get())
        except tk.TclError:pass
        return "break"
    def add(self):
        i=self.selected()
        if i is None:self.rows.append({"time":0.0,**defaults()});new=len(self.rows)-1
        else:self.rows.insert(i+1,dict(self.rows[i]));new=i+1
        self.refresh();self.tree.selection_set(str(new));self.tree.focus(str(new));self.tree.see(str(new))
    def duplicate(self):
        i=self.selected()
        if i is not None:self.rows.insert(i+1,dict(self.rows[i]));self.refresh();self.tree.selection_set(str(i+1))
    def delete(self):
        i=self.selected()
        if i is not None:self.rows.pop(i);self.refresh()
    def import_(self):
        p=filedialog.askopenfilename(parent=self.w,filetypes=[("TXT","*.txt")]);
        if p:
            try:self.rows=load_timeline(p);self.path=p;self.refresh()
            except Exception as e:messagebox.showerror("読込エラー",str(e),parent=self.w)
    def save(self):
        if not self.path:return self.save_as()
        save_timeline(self.path,self.rows);messagebox.showinfo("保存","保存しました",parent=self.w)
    def save_as(self):
        p=filedialog.asksaveasfilename(parent=self.w,defaultextension=".txt",filetypes=[("TXT","*.txt")]);
        if p:self.path=p;self.save()
    def apply(self):
        if not self.rows:return
        self.app.timeline=sorted((dict(r) for r in self.rows),key=lambda r:r["time"]);self.app.timeline_path=self.path;self.app.refresh_step_overview();self.app.save_cfg();self.app.apply_timeline(self.app.position(),True);self.app.log("エディターのタイムラインを反映");self.w.destroy()

if __name__=="__main__":
    root=tk.Tk();App(root);root.mainloop()
