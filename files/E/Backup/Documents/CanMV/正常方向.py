import sensor, image, time, lcd

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

clock = time.clock()

while True:
    clock.tick()
    img = sensor.snapshot()

    # ===== 尝试不同的参数组合 =====
    #  y_rotation=180 （水平和垂直都翻转）
    img = img.rotation_corr(y_rotation=180)

    lcd.display(img)
    print(clock.fps())
