import subprocess
import signal
import os
import sys

# グローバル変数で再生プロセスと実行フラグを管理
current_process = None
is_active = True

def cleanup_notification():
    """通知を確実に消去する。起動時や終了時に呼び出す。"""
    try:
        # check=False: 削除するものが見つからなくてエラーになっても無視する
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
    
    # 再生中のプロセスがあれば強制終了して音を止める
    if current_process is not None:
        try:
            current_process.terminate()
            # プロセスが完全に死ぬのを少しだけ待つ
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
    """シグナルハンドラの設定（メインスレッドで実行必須）"""
    # SIGUSR1 (通知ボタンからの停止命令)
    signal.signal(signal.SIGUSR1, stop_handler)
    # SIGINT (Ctrl+Cによる強制終了) も同じハンドラで受けて、finallyブロックへ誘導する
    signal.signal(signal.SIGINT, stop_handler)
    print("シグナルハンドラ設定完了。(SIGUSR1, SIGINT -> stop_handler)")

def beep():
    global current_process, is_active
    
    # 1. 念のため以前の古い通知を消す
    cleanup_notification()

    # ループ再開のためにフラグをリセット
    is_active = True
    
    # 自身のPIDを取得
    pid = os.getpid()
    
    # killコマンドのフルパスを明示（Termux環境用）
    # 通常の"kill"だとパスが通っておらず、ボタンを押しても失敗することがあるため
    kill_cmd = "kill"
    if os.path.exists("/data/data/com.termux/files/usr/bin/kill"):
        kill_cmd = "/data/data/com.termux/files/usr/bin/kill"

    # 通知を作成
    # アクション: ボタンを押すとシェル経由で kill -SIGUSR1 <PID> を実行
    title = "Beep Alert"
    content = f"ブザー再生中... 停止するにはボタンを押してください (PID:{pid})"
    button_text = "停止"
    action_command = f"{kill_cmd} -SIGUSR1 {pid}" 
    
    notification_cmd = [
        "termux-notification",
        "--id", "beep_alert",  # IDを指定 (後で消すため必須)
        "--title", title,
        "--content", content,
        "--button1", button_text,
        "--button1-action", action_command,
        "--ongoing"  # 通知を消せないように固定
    ]
    
    try:
        # check=False: 通知作成に失敗してもブザー機能だけは動かすため
        subprocess.run(notification_cmd, check=False)
    except FileNotFoundError:
        print("警告: termux-notification コマンドが見つかりません。")
    except Exception as e:
        print(f"警告: 通知の作成で予期せぬエラーが発生しました: {e}")

    print(f"ブザー再生開始... 停止は通知ボタンか Ctrl+C (PID: {pid})")

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
        # ここが必ず実行されるようにする
        print("終了処理中... 通知を削除します。")
        cleanup_notification()
        is_active = False # 安全のため
        print("停止しました。")

if __name__ == "__main__":
    setup_signal()
    beep()