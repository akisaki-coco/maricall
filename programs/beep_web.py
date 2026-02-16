import subprocess
import signal
import os
import sys
import time
import threading

# グローバル変数で再生プロセスと実行フラグを管理
current_process = None
is_active = False

def stop_handler(signum, frame):
    """停止シグナルを受け取った時の処理"""
    print(f"\n停止シグナル({signum})を受信。")
    stop_buzzer_logic()

def stop_buzzer_logic():
    """ブザー停止のメインロジック"""
    global is_active, current_process
    print("停止ロジックを実行中...")
    is_active = False
    
    # 再生中のプロセスがあれば強制終了
    if current_process:
        try:
            current_process.terminate()
            current_process.wait(timeout=0.5)
        except Exception:
            pass

    # 通知を消去
    cleanup_notification()

def cleanup_notification():
    """通知を確実に消去する"""
    try:
        subprocess.run(
            ["termux-notification-remove", "beep_alert"], 
            check=False, 
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def setup_signal():
    """シグナルハンドラの設定"""
    signal.signal(signal.SIGUSR1, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    print("シグナルハンドラ設定完了。(SIGUSR1, SIGINT -> stop_handler)")

def open_browser():
    """ブラウザで停止ページを開く"""
    # サーバーのアドレス（localhost:5000/stop）を開く
    url = "http://localhost:5000/stop"
    cmd = ["termux-open-url", url]
    try:
        subprocess.run(cmd, check=False)
        print(f"ブラウザを開きました: {url}")
    except FileNotFoundError:
        print("警告: termux-open-url コマンドが見つかりません。")

def beep():
    global current_process, is_active
    
    if is_active:
        print("既にブザーは鳴っています。")
        return

    cleanup_notification()
    is_active = True
    pid = os.getpid()
    
    # killコマンドのパス
    kill_cmd = "kill"
    if os.path.exists("/data/data/com.termux/files/usr/bin/kill"):
        kill_cmd = "/data/data/com.termux/files/usr/bin/kill"

    # 通知作成（ボタンでも一応止められるようにしておく）
    title = "緊急警報！"
    content = "【重要】ブラウザの赤いボタンで停止してください"
    button_text = "停止"
    action_command = f"{kill_cmd} -SIGUSR1 {pid}" 
    
    notification_cmd = [
        "termux-notification",
        "--id", "beep_alert",
        "--title", title,
        "--content", content,
        "--button1", button_text,
        "--button1-action", action_command,
        "--ongoing",
        "--priority", "high" # 優先度高
    ]
    
    try:
        subprocess.run(notification_cmd, check=False)
    except Exception:
        pass

    # ★ここがポイント: ブラウザを自動で開く
    open_browser()

    print(f"ブザー再生開始... (PID: {pid})")

    try:
        while is_active:
            # 960Hz
            if not is_active: break
            current_process = subprocess.Popen(["play", "-n", "synth", "0.65", "sine", "960"])
            current_process.wait() 
            
            # 770Hz
            if not is_active: break
            current_process = subprocess.Popen(["play", "-n", "synth", "0.65", "sine", "770"])
            current_process.wait()
            
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        stop_buzzer_logic()
        print("ブザー停止完了。")

if __name__ == "__main__":
    setup_signal()
    beep()
