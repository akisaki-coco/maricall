import subprocess
import signal
import os
import sys

# グローバル変数で再生プロセスと実行フラグを管理
current_process = None
is_active = True

def stop_handler(signum, frame):
    """シグナルを受け取った時の処理"""
    global is_active, current_process
    print("\n停止シグナルを受信しました。ループを終了します。")
    is_active = False
    
    # 再生中のプロセスがあれば強制終了
    if current_process:
        current_process.terminate()

def setup_signal():
    """シグナルレジストリへハンドラを登録（メインスレッドで叩く必要あり）"""
    # 停止シグナル(SIGUSR1)のハンドラを登録
    # 何があってもこのシグナル（SIGUSR1という名称）を受け取ると stop_handler が呼ばれるようにする
    signal.signal(signal.SIGUSR1, stop_handler)
    print("シグナルハンドラを設定しました。(SIGUSR1 -> stop_handler)")

def beep():
    global current_process, is_active
    
    # ループ再開のためにフラグをリセット
    is_active = True
    
    # 自身のPIDを取得
    # どのプログラムを止めればよいのかの識別用
    pid = os.getpid()
    
    # 通知を作成 (ボタンを押すと kill -SIGUSR1 <PID> を実行)
    # 注意: Termux:API パッケージがインストールされている必要があります
    title = "Beep Alert"
    content = "ブザー再生中... 停止するにはボタンを押してください"
    button_text = "停止"
    action_command = f"kill -SIGUSR1 {pid}" # killコマンドでこのプログラムにSIGUSR1を送る（= stop_handlerを呼ぶ）
    
    # 【重要】--ongoing を使うには --id が必須です
    # IDを指定することで、後から消すことも可能になります
    notification_cmd = [
        "termux-notification",
        "--id", "beep_alert",  # IDを追加("beep_alert"という名前の通知を作る。任意の文字列でOK)
        "--title", title,
        "--content", content,
        "--button1", button_text,
        "--button1-action", action_command,
        "--ongoing"  # 通知を消せないように固定（停止ボタンを押させるため）
    ]
    
    try:
        # check=False にして、もし通知作成に失敗してもブザー処理は続行させる（超重要）
        subprocess.run(notification_cmd, check=False)
    except FileNotFoundError:
        print("警告: termux-notification コマンドが見つかりません。Termux:APIを確認してください。")
    except Exception as e:
        print(f"警告: 通知の作成で予期せぬエラーが発生しました: {e}")

    print(f"ループ開始 (PID: {pid})。")

    try:
        while is_active:
            # os.system の代わりに subprocess.Popen を使用してプロセスを管理可能にする
            # 960Hz
            if not is_active: break
            # 再生中のプロセスをグローバル変数に保存
            # PopenはC#でいうawaitのようなもので、次の行に進む前に再生が終わるのを待たない
            current_process = subprocess.Popen(["play", "-n", "synth", "0.65", "sine", "960"])
            current_process.wait() # 再生終了を待つ
            
            # 770Hz
            if not is_active: break
            current_process = subprocess.Popen(["play", "-n", "synth", "0.65", "sine", "770"])
            current_process.wait()

    except KeyboardInterrupt:
        print("\nCtrl+Cで終了")
    finally:
        # 終了時に通知を削除する（ID指定していないため全消去の例ですが、適宜調整可能）
        # subprocess.run(["termux-notification-remove", "0"]) # IDを指定した場合
        subprocess.run(["termux-notification-remove", "beep_alert"], check=False)
        print("終了しました。")

if __name__ == "__main__":
    beep()