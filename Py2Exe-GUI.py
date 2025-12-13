import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import threading
import shutil

def select_file():
    file_path = filedialog.askopenfilename(
        title="选择要打包的Python脚本 (.py文件)",
        filetypes=[("Python files", "*.py"), ("All files", "*.*")]
    )
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)
        # 自动填充输出目录为脚本所在文件夹
        auto_output_dir = os.path.dirname(file_path)
        entry_output.delete(0, tk.END)
        entry_output.insert(0, auto_output_dir)

def select_output():
    output_dir = filedialog.askdirectory(title="选择输出目录")
    if output_dir:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, output_dir)

def build_exe():
    script_path = entry_file.get().strip()
    output_dir = entry_output.get().strip()

    if not script_path or not os.path.isfile(script_path):
        messagebox.showerror("错误", "请选择有效的Python脚本文件！")
        return

    if not output_dir or not os.path.isdir(output_dir):
        messagebox.showerror("错误", "请选择有效的输出目录！")
        return

    onefile = var_onefile.get()
    windowed = var_windowed.get()

    # 构建PyInstaller命令
    cmd = ["pyinstaller", "--clean", "--distpath", output_dir]

    if onefile:
        cmd.append("--onefile")

    if windowed:
        cmd.append("--windowed")
    else:
        cmd.append("--console")

    cmd.append(script_path)

    # 清空并显示日志
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "开始打包...\n\n")
    log_text.insert(tk.END, "执行命令： " + " ".join(cmd) + "\n\n")
    log_text.see(tk.END)
    log_text.update_idletasks()

    # 禁用打包按钮，防止重复点击
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

            # 清理临时文件
            work_dir = os.path.dirname(script_path)
            build_dir = os.path.join(work_dir, "build")
            spec_file = os.path.join(work_dir, os.path.basename(script_path).rsplit(".", 1)[0] + ".spec")

            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            if os.path.exists(spec_file):
                os.remove(spec_file)

            if process.returncode == 0:
                exe_name = os.path.basename(script_path).rsplit(".", 1)[0] + ".exe"
                exe_path = os.path.join(output_dir, exe_name if onefile else os.path.basename(script_path).rsplit(".", 1)[0], exe_name)
                log_text.insert(tk.END, "\n打包成功！\n")
                log_text.insert(tk.END, f"EXE 文件位置：{exe_path}\n")
                messagebox.showinfo("成功", f"打包完成！\nEXE 文件已保存至：\n{exe_path}")
            else:
                log_text.insert(tk.END, "\n打包失败，请查看上方日志。\n")
                messagebox.showerror("失败", "打包过程中出现错误，请查看日志详情。")

        except Exception as e:
            log_text.insert(tk.END, f"\n异常：{str(e)}\n")
            messagebox.showerror("异常", f"运行 PyInstaller 时发生错误：{str(e)}")

        finally:
            # 恢复界面
            progress_bar.stop()
            btn_build.config(state="normal")

    # 子线程执行打包
    threading.Thread(target=run_packaging, daemon=True).start()

# 主窗口
root = tk.Tk()
root.title("PyInstaller 可视化打包工具 v1.0")
root.geometry("720x580")
root.resizable(False, False)

# 主框架
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# 标题
title_label = ttk.Label(main_frame, text="Python 脚本打包为 EXE", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=(0, 20))

# 输入区域
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

# 选项区域
options_frame = ttk.LabelFrame(main_frame, text=" 打包选项 ", padding="15")
options_frame.pack(fill=tk.X, pady=(0, 20))

var_onefile = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="打包为单个 EXE 文件（--onefile）", variable=var_onefile).pack(anchor=tk.W, pady=5)

var_windowed = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="无控制台窗口（--windowed，推荐用于GUI程序）", variable=var_windowed).pack(anchor=tk.W, pady=5)

# 开始打包按钮
btn_build = ttk.Button(main_frame, text="开始打包", command=build_exe, style="Accent.TButton")
btn_build.pack(pady=10)

# 进度条
progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
progress_bar.pack(fill=tk.X, pady=(0, 15))

# 日志区域
log_frame = ttk.LabelFrame(main_frame, text=" 打包日志 ", padding="10")
log_frame.pack(fill=tk.BOTH, expand=True)

log_text = tk.Text(log_frame, height=12, font=("Consolas", 10))
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.configure(yscrollcommand=scrollbar.set)

# 初始化提示
log_text.insert(tk.END, "就绪。请选择脚本文件后点击“开始打包”。\n")
log_text.insert(tk.END, "打包过程中请勿关闭窗口。\n")

root.mainloop()
