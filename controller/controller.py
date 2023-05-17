import ctypes
import hashlib
import os.path
import shutil
import subprocess
import time
import winreg
import psutil

from admin.malware_tools import *


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
        self.malware = MalwareTool.json_to_list("./malware.json")

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
        for i in self.software_list:
            print(i)

    def __find_software_by_name(self, software_name):
        for s in self.software_list:
            if s[0] == software_name:
                return True
        return False

    def uninstall_software(self, software_name):
        for s_name, s_version, s_uninstall, s_feature in self.software_list:
            if s_name == software_name:
                if self.__uninstall_software(s_name, s_uninstall):
                    self.get_installed_software()
                    if self.__find_software_by_name(software_name):
                        return False
        return True

    def __uninstall_software(self, software_name: str, uninstall_path: str):
        try:
            r_path = uninstall_path
            uninstall_path = uninstall_path.replace("\\", "\\\\")
            process = subprocess.Popen(uninstall_path, shell=True)
            process.wait()
            time.sleep(1)
            for p in Controller.get_all_process():
                for c in p.cmdline():
                    if c in ['C:\\ProgramData\\Microsoft\\Search\\Data\\Temp\\usgthrsvc']:
                        continue
                    if Controller.get_file_md5(r_path) == Controller.get_file_md5(c):
                        self.uninstall_process.append(p)

            psutil.wait_procs(self.uninstall_process)
            print("调用软件卸载结束")
            if self.uninstall_process:
                self.uninstall_process.pop(0)
            return True
        except Exception as e:
            if "csrss.exe" in str(e):
                print("卸载过程涉及安全软件中间处理，可能已经通过非正常手段卸载")
                if self.safe_clear_reg(software_name):
                    return True
            elif "\'NoneType\' object has no attribute \'replace\'" in str(e):
                if self.safe_clear_reg(software_name):
                    return True
            else:
                print("软件卸载失败:", e)
            if self.uninstall_process:
                self.uninstall_process.pop(0)
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

    def is_malware_by_feature(self, name, feature):
        if not self.malware:
            return False
        for s in filter(lambda x: x.name == name, self.malware):
            for v in s.versions:
                if feature == v.feature:
                    return True
        return False

    def get_malware_folder(self, name, version):
        for m in self.malware:
            if m.name == name:
                for sv in m.versions:
                    print(sv.version, version)
                    if sv.version == version:
                        for f in sv.paths:
                            if os.path.exists(f):
                                return sv.paths
                        break
                break
        return []

    @staticmethod
    def safe_delete_folder(folder):
        try:
            # 解析用户目录路径
            folder = os.path.expanduser(folder)
            # 检查是否具有删除权限
            if not os.access(folder, os.W_OK):
                print("没有删除权限")
                return
            # 检查文件夹是否存在
            if not os.path.exists(folder):
                print("文件夹不存在")
                return
            # 删除文件夹及其内容
            shutil.rmtree(folder)
            print("文件夹删除成功")
        except Exception as e:
            print(f"文件夹删除出错: {e}")

    def safe_clear_reg(self, name):
        print(name)
        # 指定卸载项的根键
        root_key = winreg.HKEY_LOCAL_MACHINE
        for uninstall_key_path in self.__sub_keys:
            # 打开卸载项的根键
            uninstall_key = winreg.OpenKey(root_key, uninstall_key_path)
            # 遍历注册表项
            for i in range(winreg.QueryInfoKey(uninstall_key)[0]):
                sub_key_name = winreg.EnumKey(uninstall_key, i)
                sub_key_path = os.path.join(uninstall_key_path, sub_key_name)
                sub_key = winreg.OpenKey(root_key, sub_key_path)
                try:
                    # 读取 DisplayName 值
                    display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                    # 检查软件名称是否匹配
                    if display_name == name:
                        # 读取 DisplayIcon 值
                        display_icon = winreg.QueryValueEx(sub_key, "DisplayIcon")[0]
                        # 删除 DisplayIcon 路径文件
                        if display_icon:
                            icon_path = display_icon.split(",")[0]
                            if os.path.exists(icon_path):
                                os.remove(icon_path)
                        # 删除注册表项
                        winreg.DeleteKey(root_key, sub_key_path)
                        return True
                except OSError:
                    # 忽略无法访问的注册表项
                    continue
        return False

    @staticmethod
    def is_admin():
        try:
            # 调用 Windows API 获取当前进程的访问令牌信息
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            print(f"{e}")
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
        __invalid = []
        process_list = psutil.process_iter()
        for process in process_list:
            try:
                # 获取进程的名称和进程ID
                process_name = process.name()
                process_id = process.pid
                __invalid.append((process_name, process_id))
                yield process
            except psutil.AccessDenied:
                # 处理访问被拒绝的进程
                pass
