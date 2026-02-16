from gpiozero import LED
import time
import signal
import sys

led = LED(23)  # GPIO23にLEDを接続
signal.signal(signal.SIGTERM, destroy) # terminateシグナルを受け取ったときにdestroy関数を呼び出す

def destroy(signum, frame):
    print("\nLED点滅を終了します")
    led.off()
    sys.exit(0)

try:
    while True:
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

except Exception as e:
    print(f"エラーが発生しました: {e}")
    led.off()