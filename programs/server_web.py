from flask import Flask, render_template, jsonify
import beep_web
import threading

app = Flask(__name__)

# グローバル変数としてブザーの制御スレッドを持つ
buzzer_thread = None

@app.route('/')
def index():
    return "Maricall Web Server is running."

# 停止ボタン画面
@app.route('/stop')
def stop_page():
    return render_template('stop.html')

# API: ブザー停止
@app.route('/api/stop_buzzer')
def api_stop_buzzer():
    print("--------------------------------")
    print("【受信】Web画面から停止ボタンが押されました")
    # beep_web の停止ロジックを呼び出す
    beep_web.is_active = False 
    if beep_web.current_process:
        try:
            beep_web.current_process.terminate()
        except:
            pass
    beep_web.cleanup_notification()
    print("ブザー停止処理完了")
    print("--------------------------------")
    return "STOPPED"

# ラズパイからの通知を受け取るエンドポイント
@app.route('/button_pressed')
def receive_signal():
    global buzzer_thread
    print("--------------------------------")
    print("【受信】 ラズパイからボタン信号を受信！")
    
    # すでに鳴っている場合は無視するか、再起動するか？
    if beep_web.is_active:
        print("既にブザーは鳴っています")
        return "BUSY"

    print("ブザーと警告画面を起動します...")
    
    # ブザーは無限ループで実行されるため、メインスレッドをブロックしないように
    # 別のスレッドで実行する
    buzzer_thread = threading.Thread(target=beep_web.beep)
    buzzer_thread.daemon = True # サーバー終了時に道連れにする
    buzzer_thread.start()
    
    print("--------------------------------")
    return "HELLO_WEB"

if __name__ == '__main__':
    # サーバー起動時にシグナル設定（Ctrl+C用）
    beep_web.setup_signal()
    
    # 外部公開
    app.run(host='0.0.0.0', port=5000)
