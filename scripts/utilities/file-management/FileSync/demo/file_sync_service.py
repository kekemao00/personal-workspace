#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件同步服务管理器 v2.0
Python版本的批处理脚本替代方案
"""

import os
import sys
import time
import subprocess
import threading
import shutil
import signal
import json
from datetime import datetime
from pathlib import Path

class FileSyncService:
    def __init__(self):
        # 配置区域 - 根据需要修改这里的参数
        self.config = {
            'SOURCE_DIR': 'SOURCE_DIR',
            'TARGET_DIR': 'TARGET_DIR', 
            'FILE_NAME': 'file.bin',
            'SERVICE_NAME': 'FileSyncService',
            'SERVICE_DISPLAY_NAME': '文件同步服务',
            'SYNC_INTERVAL': 5,  # 检查间隔（秒）
            'RETRY_DELAY': 30,   # 错误重试延迟（秒）
        }
        
        # 文件路径
        self.script_dir = Path(os.path.abspath(__file__)).parent if '__file__' in globals() else Path.cwd()
        self.log_dir = self.script_dir / 'logs'
        self.log_file = self.log_dir / f"sync_{datetime.now().strftime('%Y%m%d')}.log"
        self.pid_file = self.script_dir / 'sync.pid'
        self.config_file = self.script_dir / 'sync.config'
        
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 加载配置文件
        self.load_config()
        
        # 服务运行标志
        self.running = False
        self.service_thread = None
        
    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                self.log("配置文件加载成功")
            except Exception as e:
                self.log(f"配置文件加载失败: {e}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.log("配置文件保存成功")
        except Exception as e:
            self.log(f"配置文件保存失败: {e}")
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def check_environment(self):
        """检查环境"""
        source_dir = Path(self.config['SOURCE_DIR'])
        target_dir = Path(self.config['TARGET_DIR'])
        
        if not source_dir.exists():
            self.log(f"错误: 源目录不存在 - {source_dir}")
            return False
        
        if not target_dir.exists():
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                self.log(f"创建目标目录: {target_dir}")
            except Exception as e:
                self.log(f"错误: 无法创建目标目录 - {target_dir}: {e}")
                return False
        
        return True
    
    def sync_file(self):
        """同步文件"""
        source_file = Path(self.config['SOURCE_DIR']) / self.config['FILE_NAME']
        target_file = Path(self.config['TARGET_DIR']) / self.config['FILE_NAME']
        
        try:
            if source_file.exists():
                # 检查文件是否需要更新
                need_sync = True
                if target_file.exists():
                    source_mtime = source_file.stat().st_mtime
                    target_mtime = target_file.stat().st_mtime
                    need_sync = source_mtime > target_mtime
                
                if need_sync:
                    shutil.copy2(source_file, target_file)
                    self.log(f"文件同步成功: {source_file} -> {target_file}")
                    return True
                else:
                    return True  # 文件已是最新
            else:
                self.log(f"警告: 源文件不存在 - {source_file}")
                return False
        except Exception as e:
            self.log(f"文件同步失败: {e}")
            return False
    
    def service_worker(self):
        """服务工作线程"""
        self.log("=== 文件同步服务启动 ===")
        
        # 记录启动时间
        with open(self.pid_file, 'w') as f:
            f.write(f"{os.getpid()}\n{datetime.now()}")
        
        # 环境检查
        if not self.check_environment():
            self.log("环境检查失败，服务退出")
            return
        
        # 服务主循环
        while self.running:
            try:
                self.sync_file()
                time.sleep(self.config['SYNC_INTERVAL'])
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"服务运行错误: {e}")
                time.sleep(self.config['RETRY_DELAY'])
        
        self.log("=== 文件同步服务停止 ===")
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def install_service(self):
        """安装服务"""
        print("\n正在安装文件同步服务...")
        self.log(f"开始安装服务: {self.config['SERVICE_NAME']}")
        
        # 在Linux系统上创建systemd服务文件
        if os.name != 'nt':
            service_content = f"""[Unit]
Description={self.config['SERVICE_DISPLAY_NAME']}
After=network.target

[Service]
Type=simple
User=root
ExecStart={sys.executable} {self.script_dir / 'file_sync_service.py'} service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            service_file = f"/etc/systemd/system/{self.config['SERVICE_NAME'].lower()}.service"
            try:
                with open(service_file, 'w') as f:
                    f.write(service_content)
                
                subprocess.run(['systemctl', 'daemon-reload'], check=True)
                subprocess.run(['systemctl', 'enable', f"{self.config['SERVICE_NAME'].lower()}"], check=True)
                
                print("✓ 服务安装成功！")
                self.log(f"服务安装成功: {self.config['SERVICE_NAME']}")
                
                start_now = input("\n是否立即启动服务？ (Y/N): ").strip().upper()
                if start_now == 'Y':
                    self.start_service()
                    
            except Exception as e:
                print(f"✗ 服务安装失败: {e}")
                self.log(f"服务安装失败: {e}")
        else:
            print("Windows服务安装需要额外的工具，建议使用手动启动模式")
    
    def uninstall_service(self):
        """卸载服务"""
        print("\n正在卸载文件同步服务...")
        self.log(f"开始卸载服务: {self.config['SERVICE_NAME']}")
        
        if os.name != 'nt':
            try:
                service_name = f"{self.config['SERVICE_NAME'].lower()}"
                subprocess.run(['systemctl', 'stop', service_name], check=False)
                subprocess.run(['systemctl', 'disable', service_name], check=False)
                
                service_file = f"/etc/systemd/system/{service_name}.service"
                if os.path.exists(service_file):
                    os.remove(service_file)
                
                subprocess.run(['systemctl', 'daemon-reload'], check=True)
                
                print("✓ 服务卸载成功！")
                self.log(f"服务卸载成功: {self.config['SERVICE_NAME']}")
                
                if self.pid_file.exists():
                    self.pid_file.unlink()
                    
            except Exception as e:
                print(f"✗ 服务卸载失败: {e}")
                self.log(f"服务卸载失败: {e}")
    
    def start_service(self):
        """启动服务"""
        print("\n正在启动文件同步服务...")
        self.log(f"启动服务: {self.config['SERVICE_NAME']}")
        
        if os.name != 'nt':
            try:
                service_name = f"{self.config['SERVICE_NAME'].lower()}"
                result = subprocess.run(['systemctl', 'start', service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✓ 服务启动成功！")
                    self.log(f"服务启动成功: {self.config['SERVICE_NAME']}")
                    time.sleep(2)
                    self.check_status()
                else:
                    print(f"✗ 服务启动失败: {result.stderr}")
                    self.log(f"服务启动失败: {result.stderr}")
            except Exception as e:
                print(f"✗ 服务启动失败: {e}")
                self.log(f"服务启动失败: {e}")
        else:
            # Windows或手动模式
            if not self.running:
                self.running = True
                self.service_thread = threading.Thread(target=self.service_worker)
                self.service_thread.daemon = True
                self.service_thread.start()
                print("✓ 服务启动成功！（手动模式）")
                self.log(f"服务启动成功（手动模式）: {self.config['SERVICE_NAME']}")
    
    def stop_service(self):
        """停止服务"""
        print("\n正在停止文件同步服务...")
        self.log(f"停止服务: {self.config['SERVICE_NAME']}")
        
        if os.name != 'nt':
            try:
                service_name = f"{self.config['SERVICE_NAME'].lower()}"
                result = subprocess.run(['systemctl', 'stop', service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✓ 服务停止成功！")
                    self.log(f"服务停止成功: {self.config['SERVICE_NAME']}")
                else:
                    print(f"✗ 服务停止失败: {result.stderr}")
                    self.log(f"服务停止失败: {result.stderr}")
            except Exception as e:
                print(f"✗ 服务停止失败: {e}")
                self.log(f"服务停止失败: {e}")
        else:
            # 手动模式
            if self.running:
                self.running = False
                print("✓ 服务停止成功！（手动模式）")
                self.log(f"服务停止成功（手动模式）: {self.config['SERVICE_NAME']}")
                if self.pid_file.exists():
                    self.pid_file.unlink()
    
    def restart_service(self):
        """重启服务"""
        print("\n正在重启文件同步服务...")
        self.stop_service()
        time.sleep(3)
        self.start_service()
    
    def check_status(self):
        """检查状态"""
        print("\n==========================================")
        print("服务状态检查")
        print("==========================================")
        
        # 检查服务状态
        service_status = "未知"
        if os.name != 'nt':
            try:
                service_name = f"{self.config['SERVICE_NAME'].lower()}"
                result = subprocess.run(['systemctl', 'is-active', service_name], 
                                      capture_output=True, text=True)
                service_status = result.stdout.strip()
            except:
                service_status = "未安装"
        else:
            service_status = "运行中" if self.running else "已停止"
        
        print(f"服务名称: {self.config['SERVICE_NAME']}")
        print(f"显示名称: {self.config['SERVICE_DISPLAY_NAME']}")
        print(f"当前状态: {service_status}")
        
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    content = f.read().strip().split('\n')
                    if len(content) >= 2:
                        print(f"进程ID: {content[0]}")
                        print(f"启动时间: {content[1]}")
            except:
                pass
        
        print(f"源目录: {self.config['SOURCE_DIR']}")
        print(f"目标目录: {self.config['TARGET_DIR']}")
        print(f"同步文件: {self.config['FILE_NAME']}")
        print(f"日志文件: {self.log_file}")
        
        # 检查目录状态
        source_dir = Path(self.config['SOURCE_DIR'])
        target_dir = Path(self.config['TARGET_DIR'])
        source_file = source_dir / self.config['FILE_NAME']
        target_file = target_dir / self.config['FILE_NAME']
        
        print(f"{'✓' if source_dir.exists() else '✗'} 源目录存在")
        print(f"{'✓' if target_dir.exists() else '✗'} 目标目录存在")
        
        if source_file.exists():
            stat = source_file.stat()
            print(f"✓ 源文件存在")
            print(f"  文件大小: {stat.st_size} 字节")
            print(f"  修改时间: {datetime.fromtimestamp(stat.st_mtime)}")
        else:
            print("✗ 源文件不存在")
        
        if target_file.exists():
            stat = target_file.stat()
            print(f"✓ 目标文件存在")
            print(f"  文件大小: {stat.st_size} 字节")
            print(f"  修改时间: {datetime.fromtimestamp(stat.st_mtime)}")
        else:
            print("✗ 目标文件不存在")
    
    def view_logs(self):
        """查看日志"""
        print("\n==========================================")
        print("查看同步日志")
        print("==========================================")
        
        if self.log_file.exists():
            print("最新日志内容 (最后20行):")
            print("------------------------------------------")
            
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"读取日志失败: {e}")
            
            print("------------------------------------------")
            print(f"\n完整日志文件: {self.log_file}")
            print("\n[1] 打开完整日志文件")
            print("[2] 清空日志文件")
            print("[3] 返回主菜单")
            
            choice = input("\n请选择操作: ").strip()
            
            if choice == "1":
                try:
                    if os.name == 'nt':
                        os.startfile(str(self.log_file))
                    else:
                        subprocess.run(['xdg-open', str(self.log_file)])
                except:
                    print(f"请手动打开日志文件: {self.log_file}")
            elif choice == "2":
                try:
                    with open(self.log_file, 'w') as f:
                        f.write("")
                    print("日志文件已清空")
                    time.sleep(2)
                except Exception as e:
                    print(f"清空日志失败: {e}")
        else:
            print(f"日志文件不存在: {self.log_file}")
            input("\n按回车键继续...")
    
    def test_sync(self):
        """测试同步"""
        print("\n==========================================")
        print("测试同步功能")
        print("==========================================")
        
        if not self.check_environment():
            print("环境检查失败，无法执行测试")
            input("\n按回车键继续...")
            return
        
        print("执行一次性同步测试...")
        
        if self.sync_file():
            print("✓ 同步测试成功！")
        else:
            print("✗ 同步测试失败！")
        
        input("\n按回车键继续...")
    
    def edit_config(self):
        """编辑配置"""
        print("\n==========================================")
        print("编辑配置")
        print("==========================================")
        
        print("当前配置:")
        for i, (key, value) in enumerate(self.config.items(), 1):
            print(f"{i}. {key}: {value}")
        
        print(f"{len(self.config) + 1}. 保存并返回")
        print(f"{len(self.config) + 2}. 取消返回")
        
        while True:
            try:
                choice = input(f"\n请选择要修改的项目 (1-{len(self.config) + 2}): ").strip()
                choice_num = int(choice)
                
                if choice_num == len(self.config) + 1:
                    self.save_config()
                    print("配置已保存！")
                    time.sleep(1)
                    break
                elif choice_num == len(self.config) + 2:
                    break
                elif 1 <= choice_num <= len(self.config):
                    key = list(self.config.keys())[choice_num - 1]
                    current_value = self.config[key]
                    new_value = input(f"请输入 {key} 的新值 (当前: {current_value}): ").strip()
                    
                    if new_value:
                        # 尝试保持原有数据类型
                        if isinstance(current_value, int):
                            try:
                                new_value = int(new_value)
                            except ValueError:
                                print("输入的不是有效数字，保持字符串类型")
                        
                        self.config[key] = new_value
                        print(f"✓ {key} 已更新为: {new_value}")
                    else:
                        print("输入为空，未修改")
                else:
                    print("无效选择，请重新输入")
            except ValueError:
                print("请输入有效数字")
            except KeyboardInterrupt:
                break
    
    def show_menu(self):
        """显示主菜单"""
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            print("\n==========================================")
            print("    Python 文件同步服务管理器 v2.0")
            print("==========================================")
            print(f"\n当前配置:")
            print(f"  源目录: {self.config['SOURCE_DIR']}")
            print(f"  目标目录: {self.config['TARGET_DIR']}")
            print(f"  同步文件: {self.config['FILE_NAME']}")
            print(f"  服务名称: {self.config['SERVICE_NAME']}")
            print(f"  日志目录: {self.log_dir}")
            print(f"\n操作选项:")
            print("  [1] 安装服务")
            print("  [2] 卸载服务")
            print("  [3] 启动服务")
            print("  [4] 停止服务")
            print("  [5] 重启服务")
            print("  [6] 查看状态")
            print("  [7] 查看日志")
            print("  [8] 编辑配置")
            print("  [9] 测试同步")
            print("  [0] 退出")
            print("\n==========================================")
            
            choice = input("请选择操作 (0-9): ").strip()
            
            try:
                if choice == "1":
                    self.install_service()
                elif choice == "2":
                    self.uninstall_service()
                elif choice == "3":
                    self.start_service()
                elif choice == "4":
                    self.stop_service()
                elif choice == "5":
                    self.restart_service()
                elif choice == "6":
                    self.check_status()
                elif choice == "7":
                    self.view_logs()
                elif choice == "8":
                    self.edit_config()
                elif choice == "9":
                    self.test_sync()
                elif choice == "0":
                    if self.running:
                        print("\n服务正在运行中，是否要停止服务后退出？(Y/N)")
                        stop_choice = input().strip().upper()
                        if stop_choice == 'Y':
                            self.stop_service()
                    print("再见！")
                    break
                else:
                    print("无效选择，请重新输入...")
                    time.sleep(2)
                    continue
                
                if choice != "6":  # 状态检查不需要暂停
                    input("\n按回车键继续...")
            except KeyboardInterrupt:
                print("\n\n收到中断信号，正在退出...")
                if self.running:
                    self.stop_service()
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                input("按回车键继续...")

def main():
    service = FileSyncService()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            service.install_service()
        elif command == "uninstall":
            service.uninstall_service()
        elif command == "start":
            service.start_service()
        elif command == "stop":
            service.stop_service()
        elif command == "restart":
            service.restart_service()
        elif command == "status":
            service.check_status()
        elif command == "logs":
            service.view_logs()
        elif command == "config":
            service.edit_config()
        elif command == "service":
            # 作为服务运行
            service.running = True
            try:
                service.service_worker()
            except KeyboardInterrupt:
                print("收到停止信号")
            finally:
                service.running = False
        else:
            print(f"未知命令: {command}")
            print("可用命令: install, uninstall, start, stop, restart, status, logs, config, service")
    else:
        # 显示交互式菜单
        service.show_menu()

if __name__ == "__main__":
    main()