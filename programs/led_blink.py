from gpiozero import LED
import time

led = LED(17)  # GPIO17にLEDを接続

try:
    while True:
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\nLED点滅を終了します")