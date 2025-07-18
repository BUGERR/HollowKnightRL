import win32api
import win32process
import win32gui
import ctypes

import pymem
import pymem.process


def win32_get_base():
    UnityPlayer = 0
    
    Kernel32 = ctypes.WinDLL('kernel32.dll')
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    hd = win32gui.FindWindow(None, "Hollow Knight")
    pid = win32process.GetWindowThreadProcessId(hd)[1]
    process_handle = win32api.OpenProcess(0x1F0FFF, False, pid)

    hProcess = Kernel32.OpenProcess(
    PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
    False, pid)

    def EnumProcessModulesEx(hProcess):
        buf_count = 256
        Psapi = ctypes.WinDLL('Psapi.dll')
        while True:
            LIST_MODULES_ALL = 0x03
            buf = (ctypes.wintypes.HMODULE * buf_count)()
            buf_size = ctypes.sizeof(buf)
            needed = ctypes.wintypes.DWORD()
            if not Psapi.EnumProcessModulesEx(hProcess, ctypes.byref(buf), buf_size, ctypes.byref(needed), LIST_MODULES_ALL):
                raise OSError('EnumProcessModulesEx failed')
            if buf_size < needed.value:
                buf_count = needed.value // (buf_size // buf_count)
                continue
            count = needed.value // (buf_size // buf_count)
            return map(ctypes.wintypes.HMODULE, buf[:count])
    
    hModule  = EnumProcessModulesEx(hProcess)

    for i in hModule:
        name = win32process.GetModuleFileNameEx(process_handle,i.value)
        # print(name)
        if name[-15:] == "UnityPlayer.dll":
            UnityPlayer = i.value
    
    return UnityPlayer

def get_base():
    """
    获取 UnityPlayer.dll 模块基地址
    """
    try:
        # 连接到进程
        process_name = "hollow_knight.exe"
        pm = pymem.Pymem(process_name)

        try:
            unity_module  = pymem.process.module_from_name(pm.process_handle, "UnityPlayer.dll")
            unity_address = unity_module.lpBaseOfDll

            mono_module  = pymem.process.module_from_name(pm.process_handle, "mono-2.0-bdwgc.dll")
            mono_address = mono_module.lpBaseOfDll

            # print(f"UnityPlayer 基地址: {hex(unity_address)}")

            return unity_address, mono_address

        except pymem.exception.ModuleNotFound:
            print("未找到 UnityPlayer.dll 模块")

        # 方法2：使用Win32 API（备选方案）
        print("尝试使用Win32 API获取模块基址...")

        unity_address = win32_get_base()

        return unity_address


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
        self.pm = pymem.Pymem("hollow_knight.exe")

        self.player_souls_offsets = [0x019B8900, 0x20, 0x88, 0x28, 0x190, 0xC8, 0x1CC]
        self.player_hp_offsets = [0x019B8900, 0x0, 0x10, 0x28, 0x18, 0xC8, 0x190]
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
        souls_address = self.get_address_unity(self.player_souls_offsets)
        souls = self.pm.read_int(souls_address)

        return souls

    def get_player_hp(self):
        player_hp_address = self.get_address_unity(self.player_hp_offsets)
        player_hp = self.pm.read_int(player_hp_address)
        
        return player_hp
    
    def get_player_xy(self):
        player_x_address = self.get_address_unity(self.player_x_offsets)
        player_y_address = self.get_address_unity(self.player_y_offsets)

        player_x = self.pm.read_float(player_x_address)
        player_y = self.pm.read_float(player_y_address)
        
        return player_x, player_y
    
    def get_boss_hp(self):
        try:
            boss_hp_address = self.get_address_unity(self.boss_hp_offsets)
            boss_hp = self.pm.read_int(boss_hp_address)
            
            if boss_hp > 900:
                return 901
            elif boss_hp < 0:
                return -1
            
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
                        return -1

    def get_boss_xy(self):
        boss_x_address = self.get_address_unity(self.boss_x_offsets)
        boss_y_address = self.get_address_unity(self.boss_y_offsets)

        boss_x = self.pm.read_float(boss_x_address)
        boss_y = self.pm.read_float(boss_y_address)

        return boss_x, boss_y

        

