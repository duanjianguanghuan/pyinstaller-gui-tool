import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import threading
import shutil
import urllib.request
import json

# GitHub API URL（raw JSON，无需认证）
VERSION_URL = "https://api.github.com/repos/duanjianguanghuan/pyinstaller-gui-tool/releases/latest"

CURRENT_VERSION = "1.1"

def check_version():
    def run_check():
        try:
            with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").strip("v")
                if latest_tag and latest_tag > CURRENT_VERSION:
                    messagebox.showwarning(
                        "发现新版本",
                        f"当前版本：{CURRENT_VERSION}\n最新版本：{latest_tag}\n\n请访问 GitHub 下载最新版：\n"
                        "https://github.com/duanjianguanghuan/pyinstaller-gui-tool/releases"
                    )
                else:
                    log_text.insert(tk.END, "已是最新版本。\n")
        except urllib.error.URLError:
            log_text.insert(tk.END, "网络连接失败，无法检查版本更新。\n")
        except Exception as e:
            log_text.insert(tk.END, f"版本检查出错：{str(e)}\n")

    threading.Thread(target=run_check, daemon=True).start()
    log_text.insert(tk.END, "正在检查版本更新...\n")
    log_text.see(tk.END)

def select_file():
    file_path = filedialog.askopenfilename(
        title="选择要打包的Python脚本 (.py文件)",
        filetypes=[("Python files", "*.py"), ("All files", "*.*")]
    )
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)
        if not entry_output.get().strip():
            entry_output.delete(0, tk.END)
            entry_output.insert(0, os.path.dirname(file_path))

def select_output():
    output_dir = filedialog.askdirectory(title="选择输出目录")
    if output_dir:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, output_dir)

def build_exe():
    script_path = entry_file.get().strip()
    output_dir = entry_output.get().strip()

    if not script_path:
        messagebox.showerror("错误", "请选择要打包的Python脚本文件！")
        return
    if not os.path.isfile(script_path):
        messagebox.showerror("错误", "脚本文件路径无效或不存在！")
        return

    if not output_dir:
        messagebox.showerror("错误", "请选择输出目录！")
        return
    if not os.path.isdir(output_dir):
        messagebox.showerror("错误", "输出目录路径无效或不存在！")
        return

    onefile = var_onefile.get()
    windowed = var_windowed.get()

    cmd = ["pyinstaller", "--clean", "--distpath", output_dir]

    if onefile:
        cmd.append("--onefile")

    if windowed:
        cmd.append("--windowed")
    else:
        cmd.append("--console")

    cmd.append(script_path)

    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "开始打包...\n\n")
    log_text.insert(tk.END, "执行命令： " + " ".join(cmd) + "\n\n")
    log_text.see(tk.END)

    btn_build.config(state="disabled")
    progress_bar.start()

    def run_packaging():
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                log_text.insert(tk.END, line)
                log_text.see(tk.END)
                log_text.update_idletasks()

            process.wait()

            work_dir = os.path.dirname(script_path)
            build_dir = os.path.join(work_dir, "build")
            spec_name = os.path.basename(script_path).rsplit(".", 1)[0] + ".spec"
            spec_path = os.path.join(work_dir, spec_name)

            if os.path.exists(build_dir):
                shutil.rmtree(build_dir, ignore_errors=True)
            if os.path.exists(spec_path):
                os.remove(spec_path)

            if process.returncode == 0:
                base_name = os.path.basename(script_path).rsplit(".", 1)[0]
                if onefile:
                    exe_path = os.path.join(output_dir, base_name + ".exe")
                else:
                    exe_path = os.path.join(output_dir, base_name, base_name + ".exe")

                log_text.insert(tk.END, "\n=== 打包成功 ===\n")
                log_text.insert(tk.END, f"EXE 文件位置：{exe_path}\n")
                messagebox.showinfo("成功", f"打包完成！\n\nEXE 文件已保存至：\n{exe_path}")
            else:
                log_text.insert(tk.END, "\n=== 打包失败 ===\n请查看上方日志查找错误原因。\n")
                messagebox.showerror("失败", "打包过程中出现错误，请查看日志详情。")

        except FileNotFoundError:
            log_text.insert(tk.END, "\n错误：未找到 pyinstaller 命令。\n请确保已安装 PyInstaller（pip install pyinstaller）\n")
            messagebox.showerror("错误", "未找到 pyinstaller。\n请在终端运行：pip install pyinstaller")
        except Exception as e:
            log_text.insert(tk.END, f"\n异常：{str(e)}\n")
            messagebox.showerror("异常", f"运行 PyInstaller 时发生错误：{str(e)}")

        finally:
            progress_bar.stop()
            btn_build.config(state="normal")

    threading.Thread(target=run_packaging, daemon=True).start()

# 主窗口
root = tk.Tk()
root.title(f"PyInstaller 可视化打包工具 v{CURRENT_VERSION}")
root.geometry("720x620")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

title_frame = ttk.Frame(main_frame)
title_frame.pack(pady=(0, 20))

title_label = ttk.Label(title_frame, text="Python 脚本打包为 EXE", font=("Segoe UI", 16, "bold"))
title_label.pack()

version_btn = ttk.Button(title_frame, text="检查更新", command=check_version)
version_btn.pack(pady=5)

input_frame = ttk.LabelFrame(main_frame, text=" 基本设置 ", padding="15")
input_frame.pack(fill=tk.X, pady=(0, 15))

ttk.Label(input_frame, text="主脚本文件：").grid(row=0, column=0, sticky=tk.W, pady=8)
entry_file = ttk.Entry(input_frame, width=65)
entry_file.grid(row=0, column=1, padx=10, pady=8)
ttk.Button(input_frame, text="浏览...", command=select_file).grid(row=0, column=2, pady=8)

ttk.Label(input_frame, text="输出目录：").grid(row=1, column=0, sticky=tk.W, pady=8)
entry_output = ttk.Entry(input_frame, width=65)
entry_output.grid(row=1, column=1, padx=10, pady=8)
ttk.Button(input_frame, text="浏览...", command=select_output).grid(row=1, column=2, pady=8)

options_frame = ttk.LabelFrame(main_frame, text=" 打包选项 ", padding="15")
options_frame.pack(fill=tk.X, pady=(0, 20))

var_onefile = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="打包为单个 EXE 文件（--onefile）", variable=var_onefile).pack(anchor=tk.W, pady=5)

var_windowed = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="无控制台窗口（--windowed，推荐用于GUI程序）", variable=var_windowed).pack(anchor=tk.W, pady=5)

btn_build = ttk.Button(main_frame, text="开始打包", command=build_exe, style="Accent.TButton")
btn_build.pack(pady=10)

progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
progress_bar.pack(fill=tk.X, pady=(0, 15))

log_frame = ttk.LabelFrame(main_frame, text=" 打包日志 ", padding="10")
log_frame.pack(fill=tk.BOTH, expand=True)

log_text = tk.Text(log_frame, height=12, font=("Consolas", 10))
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.configure(yscrollcommand=scrollbar.set)

log_text.insert(tk.END, f"PyInstaller 可视化打包工具 v{CURRENT_VERSION}\n")
log_text.insert(tk.END, "项目地址：https://github.com/duanjianguanghuan/pyinstaller-gui-tool\n\n")
log_text.insert(tk.END, "就绪。请选择脚本文件后点击“开始打包”。\n")
log_text.insert(tk.END, "点击上方“检查更新”可检测最新版本。\n")

# 启动时自动检查一次版本（可选，可注释掉关闭）
# check_version()

root.mainloop()
