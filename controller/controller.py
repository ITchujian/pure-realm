import ctypes
import os.path
import time
import pygetwindow as gw
import winreg
import hashlib
import psutil
import subprocess
from model.model import *


class Controller:
    def __init__(self):
        self.malware = []
        self.__sub_keys = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                           r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"]
        self.software_list = []
        self.get_installed_software()
        self.create_test()
        self.uninstall_process = []

    def create_test(self):
        sv = SoftwareVersion("v6.4", "677e839ed05058a527a84e875d87ba49", [])
        s = Software("好压 - 2345")
        s.add_version(sv)
        self.malware.append(s)

    def get_installed_software(self):
        self.software_list = []
        for sub_key in self.__sub_keys:
            uninstall_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key)
            num_sub_keys = winreg.QueryInfoKey(uninstall_key)[0]
            for i in range(num_sub_keys):
                subkey_name = winreg.EnumKey(uninstall_key, i)
                subkey = winreg.OpenKey(uninstall_key, subkey_name)
                display_name, display_version, display_version_un, display_feature = None, None, None, None
                try:
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    display_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                    display_version_un = winreg.QueryValueEx(subkey, "UninstallString")[0]
                    display_feature = Controller.get_file_md5(winreg.QueryValueEx(subkey, "DisplayIcon")[0])
                except OSError:
                    pass
                finally:
                    if (display_name, display_version, display_version_un, display_feature) == (None, None, None, None):
                        continue
                    self.software_list.append((display_name, display_version, display_version_un, display_feature))
        self.software_list = list(set(self.software_list))
        self.software_list = sorted(self.software_list, key=lambda x: x[0])
        # for i in self.software_list:
        #     print(i)

    def uninstall_software(self, software_name):
        for s_name, s_version, s_uninstall, s_feature in self.software_list:
            if s_name == software_name:
                return self.__uninstall_software(s_uninstall)
        return False

    def __uninstall_software(self, uninstall_path: str):
        r_path = uninstall_path
        uninstall_path = uninstall_path.replace("\\", "\\\\")
        try:
            process = subprocess.Popen(uninstall_path, shell=True)
            process.wait()
            for p in Controller.get_all_process():
                for c in p.cmdline():
                    if c in ['C:\\ProgramData\\Microsoft\\Search\\Data\\Temp\\usgthrsvc']:
                        continue
                    if Controller.get_file_md5(r_path) == Controller.get_file_md5(c):
                        self.uninstall_process.append(p)

            psutil.wait_procs(self.uninstall_process)
            if process.returncode == 0:
                print("软件卸载成功")
                self.uninstall_process.pop()
                return True
            else:
                print("软件卸载取消")
                self.uninstall_process.pop()
                return False
        except Exception as e:
            print("软件卸载失败:", e)
            self.uninstall_process.pop()
            return False

    def is_malware_by_name(self, name):
        if not self.malware:
            return False
        return bool(list(filter(lambda x: x.name == name, self.malware)))

    def is_malware_by_version(self, name, version):
        if not self.malware:
            return False
        for s in filter(lambda x: x.name == name, self.malware):
            if s and list(filter(lambda x: x.version == version, s.versions)):
                return True

    def is_malware_by_feature(self, feature):
        if not self.malware:
            return False
        for s in self.malware:
            for v in s.versions:
                if feature == v.feature:
                    return True
        return False

    @staticmethod
    def is_admin():
        try:
            # 调用 Windows API 获取当前进程的访问令牌信息
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    @staticmethod
    def get_file_md5(file_path):
        if not os.access(file_path, os.R_OK):
            return None
        if not os.path.exists(file_path):
            return None
        m = hashlib.md5()  # 创建md5对象
        with open(file_path, 'rb') as f_obj:
            while True:
                data = f_obj.read(4096)
                if not data:
                    break
                m.update(data)  # 更新md5对象

        return m.hexdigest()  # 返回md5对象

    @staticmethod
    def get_all_process():
        # 获取所有进程列表
        process_list = psutil.process_iter()
        for process in process_list:
            try:
                # 获取进程的名称和进程ID
                process_name = process.name()
                process_id = process.pid

                # print(f"进程名称: {process_name}")
                # print(f"进程ID: {process_id}")

                # 获取进程的其他信息，如命令行参数、父进程ID等
                cmdline = process.cmdline()
                parent_pid = process.ppid()
                yield process

                # print(f"命令行参数: {cmdline}")
                # print(f"父进程ID: {parent_pid}")
                # print("-" * 50)
            except psutil.AccessDenied:
                # 处理访问被拒绝的进程
                pass
