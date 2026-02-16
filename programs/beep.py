import os

for i in range(5):
    os.system("play -n synth 0.65 sine 960")
    os.system("play -n synth 0.65 sine 770")