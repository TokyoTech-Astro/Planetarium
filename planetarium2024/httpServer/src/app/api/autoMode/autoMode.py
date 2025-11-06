#!/usr/bin/env -S python3 -u

import json
import requests
import time
import signal
import os
from os.path import join
from dotenv import load_dotenv
from typing import Union

dotenv_path = join('./', '.env')
load_dotenv()
SERVER_LED_KOSEI = os.getenv('NEXT_PUBLIC_SERVER_LED_KOSEI')
SERVER_LED_KOSEI_PORT = os.getenv('NEXT_PUBLIC_SERVER_LED_KOSEI_PORT')
SERVER_LED = os.getenv('NEXT_PUBLIC_SERVER_LED')
SERVER_LED_PORT = os.getenv('NEXT_PUBLIC_SERVER_LED_PORT')
SERVER_MOTOR = os.getenv('NEXT_PUBLIC_SERVER_MOTOR')
SERVER_MOTOR_PORT = os.getenv('NEXT_PUBLIC_SERVER_MOTOR_PORT')
SERVER_AUDIO = os.getenv('NEXT_PUBLIC_SERVER_AUDIO')
SERVER_AUDIO_PORT = os.getenv('NEXT_PUBLIC_SERVER_AUDIO_PORT')

with open('src/k2023.json') as f:
    k2023 = json.load(f)

with open('src/leds.json') as f:
    leds = json.load(f)

def sigtermHandler(signal_number, frame):
    for led in leds:
        putLed(led['pin'], False, None)
    postMotor("stop")
    postAudio("stop")
    print("Auto mode stopped.")
    exit(0)

signal.signal(signal.SIGTERM, sigtermHandler)

black   = '\u001b[30m'
red     = '\u001b[31m'
green   = '\u001b[32m'
yellow  = '\u001b[33m'
blue    = '\u001b[34m'
magenta = '\u001b[35m'
cyan    = '\u001b[36m'
white   = '\u001b[37m'
reset   = '\u001b[0m'

name2pin = {led['name']: led['pin'] for led in leds}
pin2name = {led['pin']: led['name'] for led in leds}

def putLed(pin:int, state:bool, fade_time:Union[float,None]):
    # リトライ回数を追跡するためのカウンタ（オプション）
    attempt = 0 
    
    # 成功するまで無限ループ
    while True:
        attempt += 1
        res = None
        url = ''
        
        # URL組み立てロジック（恒星LEDの判定）
        # 注: このロジックは冗長なので、可能であれば前の回答の提案に従いリファクタリングすることを推奨します
        if int(pin) == name2pin['恒星']:
            base_url = f'http://{SERVER_LED_KOSEI}:{SERVER_LED_KOSEI_PORT}/led/{pin}?state={state}'
        else:
            base_url = f'http://{SERVER_LED}:{SERVER_LED_PORT}/led/{pin}?state={state}'
        
        url = base_url
        if fade_time != None:
            url += f'&fade_time={fade_time}'
        
        print(f'{cyan}INFO{reset}: Attempting PUT to {url} (Attempt {attempt})')
        
        try:
            # リクエスト実行
            res = requests.put(url, timeout=1) 
            
            # HTTPステータスコードのチェック
            if res.status_code == 200:
                print(f'{yellow}■{reset} Set LED state successful. (pin:{pin}, state:{state}). Status: {res.status_code}')
                break  # ★ 成功したらループを抜ける
            else:
                # 4xx, 5xx エラーの場合 (サーバーは応答したが処理失敗)
                print(f'{red}ERROR{reset}: Failed to set LED state (HTTP Error). URL: {url}, Status: {res.status_code}, Body: {res.text}')
                # HTTPエラーでもリトライを試みる
        
        # requestsの例外処理 (ネットワーク接続失敗、タイムアウトなど)
        except requests.exceptions.RequestException as e:
            print(f'{red}FATAL ERROR{reset}: Failed to connect to LED server. URL: {url}, Error: {e}')
        except Exception as e:
            print(f'{red}FATAL ERROR{reset}: An unexpected error occurred in putLed. Error: {e}')

        # リトライ処理
        print(f'{magenta}WAIT{reset}: Retrying in 1.0 second...')
        time.sleep(1.0) # 1秒待機してからリトライ


def handleLed(_leds:list[dict[int,float]]):
    for _led in _leds:
        pin = _led['pin']
        fade_time = _led['fade_time']
        if pin > 0:
            if fade_time == 0.0:
                putLed(pin, True, None)
            else:
                putLed(pin, True, fade_time)
        else:
            if fade_time == 0.0:
                putLed(-pin, False, None)
            else:
                putLed(-pin, False, fade_time)

def postMotor(query:str, dir:str="", deg:int=0, time_val:float=0):
    # time は Python の組み込みモジュール名と衝突するため time_val に変更することを推奨します
    
    attempt = 0 
    
    while True:
        attempt += 1
        url = f'http://{SERVER_MOTOR}:{SERVER_MOTOR_PORT}/motor?query={query}&dir={dir}&deg={deg}&time={time_val}'
        
        print(f'{cyan}INFO{reset}: Attempting POST to {url} (Attempt {attempt})')
        
        try:
            # リクエスト実行
            res = requests.post(url, timeout=1) 
            
            # HTTPステータスコードのチェック
            if res.status_code == 200:
                if query == "start":
                    print(f'{green}■{reset} Start rotation successful. (dir:{dir}, deg:{deg}, time:{time_val}). Status: {res.status_code}')
                elif query == "stop":
                    print(f'{green}■{reset} Stop rotation successful. Status: {res.status_code}')
                break  # ★ 成功したらループを抜ける
            else:
                # 4xx, 5xx エラーの場合
                print(f'{red}ERROR{reset}: Failed to control motor (HTTP Error). URL: {url}, Status: {res.status_code}, Body: {res.text}')
        
        # requestsの例外処理 (ネットワーク接続失敗、タイムアウトなど)
        except requests.exceptions.RequestException as e:
            print(f'{red}FATAL ERROR{reset}: Failed to connect to Motor server. URL: {url}, Error: {e}')
        except Exception as e:
            print(f'{red}FATAL ERROR{reset}: An unexpected error occurred in postMotor. Error: {e}')

        # リトライ処理
        print(f'{magenta}WAIT{reset}: Retrying in 1.0 second...')
        time.sleep(1.0) # 1秒待機してからリトライ


def handleMotor(motor:dict[int,float]):
    if motor['degree'] > 0:
        postMotor("start", "forward", motor['degree'], motor['time'])
    else:
        postMotor("start", "back", -motor['degree'], motor['time'])

# (SERVER_AUDIO, SERVER_AUDIO_PORT, color codes are defined externally)

def postAudio(filename:str):
    attempt = 0 
    
    while True:
        attempt += 1
        url = f'http://{SERVER_AUDIO}:{SERVER_AUDIO_PORT}/audio?filename={filename}'
        
        print(f'{cyan}INFO{reset}: Attempting POST to {url} (Attempt {attempt})')
        
        try:
            # リクエスト実行
            res = requests.post(url, timeout=1) 
            
            # HTTPステータスコードのチェック
            if res.status_code == 200:
                print(f'{blue}■{reset} Playing {filename} successful. Status: {res.status_code}')
                break  # ★ 成功したらループを抜ける
            else:
                # 4xx, 5xx エラーの場合
                print(f'{red}ERROR{reset}: Failed to play audio (HTTP Error). URL: {url}, Status: {res.status_code}, Body: {res.text}')
                
        # requestsの例外処理 (ネットワーク接続失敗、タイムアウトなど)
        except requests.exceptions.RequestException as e:
            print(f'{red}FATAL ERROR{reset}: Failed to connect to Audio server. URL: {url}, Error: {e}')
        except Exception as e:
            print(f'{red}FATAL ERROR{reset}: An unexpected error occurred in postAudio. Error: {e}')

        # リトライ処理
        print(f'{magenta}WAIT{reset}: Retrying in 1.0 second...')
        time.sleep(1.0) # 1秒待機してからリトライ

def postShootingStar(state: str):
    res = None
    url = f'http://shooting-star.local/shower?state={state}'
    try:
        print(f'{cyan}INFO{reset}: Attempting PUT to {url}')
        res = requests.put(url, timeout=1) # タイムアウト設定を追加
        
        # HTTPステータスコードのチェック
        if res.status_code == 200:
            print(f'{yellow}■{reset} Set shooting star state. (state:{state}). Response: {res.status_code}')
        else:
            print(f'{red}ERROR{reset}: Failed to set shooting star state. URL: {url}, Status: {res.status_code}, Body: {res.text}')
            
    # requestsの例外処理 (ネットワーク接続失敗、タイムアウトなど)
    except requests.exceptions.RequestException as e:
        print(f'{red}FATAL ERROR{reset}: Failed to connect to shooting star server. URL: {url}, Error: {e}')
    except Exception as e:
        print(f'{red}FATAL ERROR{reset}: An unexpected error occurred in put shooting star. Error: {e}')

def handleInterval(interval:str|int):
    if interval == "allLedOff":
        for led in leds:
            putLed(led['pin'], False, None)
    else:
        print(f'{magenta}■{reset} Interval of {interval} sec.')
        time.sleep(interval)

def autoMode():
    for i in k2023:
        print(f'\n{white}--- Processing Step ---{reset}')
        print(i)
        if i.get('star') != None:
            handleLed(i['star'])
        if i.get("motor") != None:
            handleMotor(i["motor"])
        if i.get("audio") != None:
            postAudio(i["audio"]) 
        if i.get("shooting-star") != None:
            postShootingStar(i["shooting-star"])
        if i.get("interval") != None:
            handleInterval(i["interval"])
        print("")

autoMode()