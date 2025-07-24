import mss
import numpy as np
import win32gui
import cv2

import pymem
import pymem.process
import psutil

import time
from Actions import Look_up, press_and_release_JUMP

BOSS_MAX_HP = 900


def get_client_rect():
    title = "Hollow Knight"
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"未找到窗口：{title}")

    # 1. 取客户区大小（不含边框）
    client_rect = win32gui.GetClientRect(hwnd)   # (left, top, right, bottom)
    w = client_rect[2] - client_rect[0]
    h = client_rect[3] - client_rect[1]

    # 2. 把客户区左上角转换成屏幕坐标
    left_top = win32gui.ClientToScreen(hwnd, (0, 0))
    left, top = left_top

    return {"left": left, "top": top, "width": w, "height": h}


def get_frame():
    
    monitor = get_client_rect()
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor))

        return img
    

def get_frame_rgb():

    monitor = get_client_rect()
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img
    

def get_frame_grey_resized():
    monitor = get_client_rect()
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor))[:, :, :3]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    return cv2.resize(gray, (84, 84))


#---------------------------------------------------------------------

def get_enemy_hp_bar():
    frame = get_frame_rgb()

    hp_bar_center_line = frame[640, 295:882, :]

    if (np.all(hp_bar_center_line[..., 0] == hp_bar_center_line[..., 1]) and
                np.all(hp_bar_center_line[..., 1] == hp_bar_center_line[..., 2])):
        boss_hp = (hp_bar_center_line[..., 0] < 3).sum() / len(hp_bar_center_line)
    return boss_hp




def get_pid_by_name(name):
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and name.lower() in p.info['name'].lower():
            return p.info['pid']
    raise RuntimeError(f"进程 {name} 未找到")


def get_base():
    """
    获取 UnityPlayer.dll 模块基地址
    """
    try:
        # 连接到进程
        process_name = "hollow_knight.exe"
        pid = get_pid_by_name(process_name)
        pm = pymem.Pymem(pid)

        try:
            unity_module  = pymem.process.module_from_name(pm.process_handle, "UnityPlayer.dll")
            unity_address = unity_module.lpBaseOfDll

            mono_module  = pymem.process.module_from_name(pm.process_handle, "mono-2.0-bdwgc.dll")
            mono_address = mono_module.lpBaseOfDll

            # print(f"UnityPlayer 基地址: {hex(unity_address)}")

            return unity_address, mono_address

        except pymem.exception.ModuleNotFound:
            print("未找到 UnityPlayer.dll 模块")


    except pymem.exception.ProcessNotFound:
        print(f"找不到进程: {process_name}")
        return None
    except pymem.exception.ProcessError as e:
        print(f"进程错误: {e}")
        return None
    finally:
        if 'pm' in locals():
            pm.close_process()



class HpXy_getter():
    def __init__(self):
        self.UnityPlayer, self.mono = get_base()
        self.pm = pymem.Pymem(get_pid_by_name("hollow_knight.exe"))

        self.player_souls_offsets = [0x019B8900, 0x0, 0x0, 0x10, 0x28, 0x58, 0x1CC]
        self.player_hp_offsets = [0x019B8900, 0x0, 0x0, 0x10, 0x28, 0x58, 0x190]

        self.player_x_offsets = [0x01A1DDD8, 0xAB8, 0xAA0, 0x638, 0x90, 0x140, 0xC]
        self.player_y_offsets = [0x01A1DDD8, 0xA90, 0x638, 0x0, 0x28, 0xF8, 0xC]

        self.boss_hp_offsets = [0x019D4478, 0x130, 0xD0, 0x30, 0xF8, 0x28, 0xF8, 0x140]
        self.boss_hp_offsets_backup = [0x019D4478, 0x238, 0xC0, 0x30, 0x30, 0xF8, 0x28, 0x140]
        self.boss_hp_offsets_backup_mono_1 = [0x00497DE8, 0x90, 0xE18, 0x458, 0xA0, 0x40, 0x20, 0x140]
        self.boss_hp_offsets_backup_mono_2 = [0x004A7418, 0x290, 0xAB8, 0x458, 0xA0, 0x40, 0x20, 0x140]

        self.boss_x_offsets = [0x01A1DDD8, 0xA90, 0x640, 0x140, 0x68, 0x140, 0xC]
        self.boss_y_offsets = [0x01A1DDD8, 0xA90, 0x620, 0x48, 0x140, 0x60, 0x10]

    def close_pm_process(self):
        if self.pm in locals():
            self.pm.close_process()

    def get_address_unity(self, offsets):
        """
        读取多级指针地址
        :param offsets: 偏移列表
        :return: 地址值
        """
        addr = self.pm.read_longlong(self.UnityPlayer + offsets[0])
        for offset in offsets[1:-1]:
            addr = self.pm.read_longlong(addr + offset)
        return addr + offsets[-1]
    
    def get_address_mono(self, offsets):
        addr = self.pm.read_longlong(self.mono + offsets[0])
        for offset in offsets[1:-1]:
            addr = self.pm.read_longlong(addr + offset)
        return addr + offsets[-1]
    
    def get_player_souls(self):
        try:
            souls_address = self.get_address_unity(self.player_souls_offsets)
            souls = self.pm.read_int(souls_address)

            return souls
        except pymem.exception.MemoryReadError as e:
            return 0

    def get_player_hp(self):
        player_hp_address = self.get_address_unity(self.player_hp_offsets)
        player_hp = self.pm.read_int(player_hp_address)
        
        return player_hp
    
    def get_player_xy(self):
        try:
            player_x_address = self.get_address_unity(self.player_x_offsets)
            player_y_address = self.get_address_unity(self.player_y_offsets)

            player_x = self.pm.read_float(player_x_address)
            player_y = self.pm.read_float(player_y_address)
            
            return player_x, player_y
        except pymem.exception.MemoryReadError as e:
            return 27.0, 28.3
        
    def get_boss_hp(self):
        try:
            boss_hp_address = self.get_address_unity(self.boss_hp_offsets)
            boss_hp = self.pm.read_int(boss_hp_address)
            
            return boss_hp
        
        except pymem.exception.ProcessNotFound:
            print("找不到空洞骑士进程")
            
        except pymem.exception.MemoryReadError as e:
            # print(f"boss hp 内存读取错误 查询备用地址: {e}")
            try:
                boss_hp_address = self.get_address_unity(self.boss_hp_offsets_backup)
                boss_hp = self.pm.read_int(boss_hp_address)

                return boss_hp
            except pymem.exception.MemoryReadError as e:
                # print(f"boss hp 备用地址内存读取错误: {e}")
                try:
                    boss_hp_address = self.get_address_mono(self.boss_hp_offsets_backup_mono_1)
                    boss_hp = self.pm.read_int(boss_hp_address)

                    return boss_hp
                except pymem.exception.MemoryReadError as e:
                    try:
                        boss_hp_address = self.get_address_mono(self.boss_hp_offsets_backup_mono_2)
                        boss_hp = self.pm.read_int(boss_hp_address)

                        return boss_hp
                    
                    except pymem.exception.MemoryReadError as e:

                        frame = get_frame_rgb()

                        hp_bar_center_line = frame[640, 295:882, :]

                        if (np.all(hp_bar_center_line[..., 0] == hp_bar_center_line[..., 1]) and
                                    np.all(hp_bar_center_line[..., 1] == hp_bar_center_line[..., 2])):
                            boss_hp = BOSS_MAX_HP * (hp_bar_center_line[..., 0] < 3).sum() / len(hp_bar_center_line)
                            return boss_hp
                        else:
                            return 1

    # def get_boss_xy(self):
    #     boss_x_address = self.get_address_unity(self.boss_x_offsets)
    #     boss_y_address = self.get_address_unity(self.boss_y_offsets)

    #     boss_x = self.pm.read_float(boss_x_address)
    #     boss_y = self.pm.read_float(boss_y_address)

    #     return boss_x, boss_y


#---------------------------------------------------------------------


# 应该在对战结束才执行，boss 血量判断有问题，打死boss后血量基址会变，考虑用 mod，或者用玩家坐标
def restart():

    getter = HpXy_getter()

    # 如果打完 boss 了，站起来，选难度（判断不是在打 boss） player x > 60，说明在雕像前

    while True:
        player_x, y = getter.get_player_xy()

        # 如果还在 boss 房，歇两秒再来判断是否打完
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
        station = cv2.resize(get_frame_rgb(), (1000,500))
        player_x, y = getter.get_player_xy()

        # 如果箭头指第一个难度（判断像素点），且在雕像前。按下确定进 boss
        if station[229][580][0] > 200 and player_x >= 60: 
            press_and_release_JUMP()
            print('restart')
            time.sleep(3)
            break
        # 否则选下一个难度
        else:
            Look_up()
            time.sleep(0.2)