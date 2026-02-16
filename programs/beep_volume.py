import subprocess
import signal
import os
import sys
import time
import threading
import json

# グローバル変数
current_process = None
is_active = False

def get_current_volume():
    """現在の音量（musicストリーム）を取得する"""
    try:
        # termux-volume コマンドの結果をJSONで取得
        result = subprocess.run(["termux-volume"], capture_output=True, text=True, check=True)
        volumes = json.loads(result.stdout)
        
        # Stream 'music' の音量を探す
        for v in volumes:
            if v['stream'] == 'music':
                return v['volume']
    except Exception:
        return -1 # 取得失敗
    return -1

def volume_monitor(pid):
    """音量変化を監視するスレッド"""
    global is_active
    
    # 初期音量を取得
    initial_volume = get_current_volume()
    if initial_volume == -1:
        print("警告: 音量の取得に失敗しました。音量ボタン停止機能は無効です。")
        return

    print(f"音量監視スタート (現在: {initial_volume})")

    while is_active:
        current_vol = get_current_volume()
        
        # 取得できており、かつ初期値と違う場合
        if current_vol != -1 and current_vol != initial_volume:
            print(f"\n★音量変化検知: {initial_volume} -> {current_vol}")
            print("停止トリガー発動！")
            
            # 自分自身に停止シグナル（SIGUSR1）を送る
            os.kill(pid, signal.SIGUSR1)
            break
            
        time.sleep(0.5) # 0.5秒ごとにチェック

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

def stop_handler(signum, frame):
    """停止ボタン（SIGUSR1）またはCtrl+C（SIGINT）を受け取った時の処理"""
    global is_active, current_process
    print(f"\n停止シグナル({signum})を受信。終了処理を開始します...")
    is_active = False
    
    if current_process is not None:
        try:
            current_process.terminate()
            current_process.wait(timeout=0.5)
            # current_processをリセット
            current_process = None
        except Exception:
            pass
    else:
        print("現在再生中のプロセスはありません。")
        print("プログラムは正常に終了します。")
        sys.exit(0)  # プロセスがない場合はすぐに終了

def setup_signal():
    """シグナルハンドラの設定"""
    signal.signal(signal.SIGUSR1, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    print("シグナルハンドラ設定完了。")

def beep():
    global current_process, is_active
    
    # 念のため通知を消す
    cleanup_notification()

    is_active = True
    pid = os.getpid()
    
    # 音量監視スレッドを開始
    monitor_thread = threading.Thread(target=volume_monitor, args=(pid,))
    monitor_thread.daemon = True
    monitor_thread.start()

    # 通知作成（ボタンでも止められるように残しておく）
    kill_cmd = "kill"
    if os.path.exists("/data/data/com.termux/files/usr/bin/kill"):
        kill_cmd = "/data/data/com.termux/files/usr/bin/kill"

    title = "緊急警報"
    content = "【音量ボタン】を押すと停止します"
    
    notification_cmd = [
        "termux-notification",
        "--id", "beep_alert",
        "--title", title,
        "--content", content,
        "--button1", "停止",
        "--button1-action", f"{kill_cmd} -SIGUSR1 {pid}",
        "--ongoing",
        "--priority", "max" # 優先度高
    ]
    
    try:
        subprocess.run(notification_cmd, check=False)
    except:
        pass

    print(f"ブザー再生開始... (PID: {pid})")
    print("----------------------------------------")
    print("  ★ スマホの音量ボタンを押すと停止します ★  ")
    print("----------------------------------------")

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
        print(f"予期せぬエラー: {e}")
    finally:
        print("終了処理中... 通知を削除します。")
        cleanup_notification()
        is_active = False
        print("停止しました。")

if __name__ == "__main__":
    setup_signal()
    beep()
