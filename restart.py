import time
from utils.capture_window import get_client_rect, capture_window
import cv2
from utils.Actions import Look_up, press_and_release_JUMP
from utils.HpXyGetter import HpXy_getter



# 应该在对战结束才执行，boss 血量判断有问题，打死boss后血量基址会变，考虑用 mod
def restart():

    getter = HpXy_getter()

    # 如果打完 boss 了，站起来，选难度（判断不是在打 boss） player x > 60，说明在雕像前

    while True:
        player_x, y = getter.get_player_xy()
        if player_x < 60 and y > 20:
            time.sleep(2)
        else:
            break

    print("over")

    time.sleep(1) 
    Look_up() # 出来躺地上，先站起来
    time.sleep(1.5)
    Look_up() # 进入选择界面
    time.sleep(1)

    while True:
        station = cv2.resize(capture_window(get_client_rect("Hollow Knight")), (1000,500))
        player_x, y = getter.get_player_xy()

        # 如果箭头指第一个难度（判断像素点），且在雕像前。按下确定进 boss
        if station[229][580][0] > 200 and player_x >= 60: 
            press_and_release_JUMP()
            print('restart')
            time.sleep(3)
            break
        else:
            Look_up()
            time.sleep(0.2)
