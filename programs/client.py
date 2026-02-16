from gpiozero import Button
from gpiozero import LED
import requests
import time
import subprocess

# ラズパイのIPアドレスを指定 (例: 192.168.1.131)
# 新規環境ではそれに応じてラズパイのIPアドレスを確認する必要あり
# ポート5000番の /button_pressed にアクセスする設定
SERVER_URL = "http://192.168.1.143:5000/"

# # 1文字だけ読み取るための関数
# def getch():
#     # 現在のターミナル設定を保存
#     fd = sys.stdin.fileno()
#     old_settings = termios.tcgetattr(fd)
#     try:
#         # ターミナルを「非カノニカルモード（Enter待たないモード）」に変更
#         tty.setraw(sys.stdin.fileno())
#         # 1文字読み取る
#         ch = sys.stdin.read(1)
#     finally:
#         # 終わったら必ず元の設定に戻す（これをしないとターミナルがおかしくなる）
#         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#     return ch

# print("ESP32シミュレーター起動")
# print("Enterキーを押すと信号を送信します (Ctrl+Cで終了)")
# print(" 'a' を押すとブザー送信")
# print(" 'b' を押すとLED送信")
# print(" 'e' を押すとハロー通信")

# try:
#     while True:
#         #キーが押されているかチェック
#         key = getch()
        
#         # 分岐処理
#         if key == "a":
#             print("ブザー送信")
#             target_url = SERVER_URL + "/buzzer"
#             try:
#                 response = requests.get(target_url)
#                 # メッセージ表示
#                 print("ラズパイからの返事：", response.text)

#                 # レスポンス確認
#                 if response.status_code == 200:
#                     print("ブザー信号送信成功")
#                 else:
#                     print(f"ブザー信号送信失敗: ステータスコード {response.status_code}")
#             except:
#                 print("通信エラー")

#         elif key == "b":
#             print("LED送信")
#             target_url = SERVER_URL + "/led"
#             try:
#                 response = requests.get(target_url)
#                 # メッセージ表示
#                 print("ラズパイからの返事：", response.text)
                
#                 # レスポンス確認
#                 if response.status_code == 200:
#                     print("ブザー信号送信成功")
#                 else:
#                     print(f"ブザー信号送信失敗: ステータスコード {response.status_code}")
#             except:
#                 print("通信エラー")

#         if key == "e":
#             print("サーバハロー送信")
#             target_url = SERVER_URL + "/button_pressed"
#             try:
#                 response = requests.get(target_url)
#                 # メッセージ表示
#                 print("ラズパイからの返事：", response.text)
                
#                 # レスポンス確認
#                 if response.status_code == 200:
#                     print("ブザー信号送信成功")
#                 else:
#                     print(f"ブザー信号送信失敗: ステータスコード {response.status_code}")
#             except:
#                 print("通信エラー")
        
# except KeyboardInterrupt:
#     print("\n終了します")

button = Button(18)  # GPIO18に接続されたボタン
pressed = False
led_process = None  # LED点滅プロセスの管理用変数

try:
    while True:
        # 1. ユーザーの入力を待つ (ボタン押下を待つ)
        if button.is_pressed:
            if pressed == False:  # ボタンが押された瞬間だけ反応させる
                pressed = True
                print("ボタンが押されました！")

                # サブプロセスでLEDを点滅させる（オプション）
                led_process = subprocess.Popen(["python3", "led_blink.py"])

                # 2. サーバーへ信号を送る
                print(f"送信中... {SERVER_URL}button_pressed")
                try:
                    response = requests.get(SERVER_URL + "button_pressed")
                    print("ラズパイからの返事：", response.text)
                    
                    if response.status_code == 200:
                        print("成功: ラズパイが反応しました")
                    else:
                        print(f"失敗: ステータスコード {response.status_code}")
                except requests.exceptions.ConnectionError:
                    print("エラー: ラズパイに繋がりません。IPアドレスは合っていますか？サーバーは動いていますか？")
        else:
            pressed = False  # ボタンが離されたらリセット
        
        # CPU負荷を下げるための待機時間
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n終了します")
    # LED点滅プロセスが動いていれば終了させる
    if led_process is not None:
        led_process.terminate()
        led_process.wait(timeout=0.5)
        led_process = None

# try:
#     while True:
#         # 1. ユーザーの入力を待つ (ボタン押下の代わり)
#         input(">> Enterキーを押してください: ")
        
#         # 2. サーバーへ信号を送る
#         print(f"送信中... {SERVER_URL}")
#         try:
#             response = requests.get(SERVER_URL)
#             print("ラズパイからの返事：", response.text)
            
#             if response.status_code == 200:
#                 print("成功: ラズパイが反応しました")
#             else:
#                 print(f"失敗: ステータスコード {response.status_code}")
                
#         except requests.exceptions.ConnectionError:
#             print("エラー: ラズパイに繋がりません。IPアドレスは合っていますか？サーバーは動いていますか？")

# except KeyboardInterrupt:
#     print("\n終了します")
