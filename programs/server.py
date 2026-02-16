from flask import Flask
import beep

app = Flask(__name__)

# http://ラズパイのIP:5000/button_pressed にアクセスが来たらここが動く
@app.route('/button_pressed')
def receive_signal():
    print("--------------------------------")
    print("【受信】 ボタンが押されました！")
    print("ブザーを鳴らします")
    beep.beep()  # ブザーを鳴らす関数を呼び出す
    print("--------------------------------")

    # 送信側に「届いたよ」と返事をする
    return "HELLO"

#窓口A：ブザー用
@app.route('/buzzer')
def ring_buzzer():
    print("【受信】ブザー用ボタンが押されました")
    return "BUZZER_OK"

#窓口B：LED用
@app.route('/led')
def light_led():
    print("【受信】LED用ボタンが押されました")
    return "LED_OK"

if __name__ == '__main__':
    # サーバーを起動する前に、メインスレッドでシグナルハンドラを設定する
    beep.setup_signal()

    # host='0.0.0.0' にしないと、外部(PC)からアクセスできないので注意
    app.run(host='0.0.0.0', port=5000)