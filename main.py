import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import threading
import yaml
import glob
import locale

class Translator:
    def __init__(self, translations_dir='translations'):
        self.translations_dir = translations_dir
        self.translations = {}
        self.current_language = self.detect_system_language()
        self.load_translations()

    def detect_system_language(self):
        # 获取系统语言，默认为英文
        system_lang = locale.getdefaultlocale()[0] or 'en_US'
        return system_lang if system_lang in ['zh_CN', 'en_US'] else 'en_US'

    def load_translations(self):
        # 扫描并加载所有翻译文件
        translation_files = glob.glob(os.path.join(self.translations_dir, '*.yaml'))
        for file_path in translation_files:
            lang_code = os.path.splitext(os.path.basename(file_path))[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = yaml.safe_load(f)

    def get_available_languages(self):
        # 获取可用语言列表
        return {lang: self.translations[lang]['language_name'] for lang in self.translations}

    def set_language(self, language_code):
        if language_code in self.translations:
            self.current_language = language_code

    def translate(self, key, **kwargs):
        # 获取翻译文本，支持格式化
        try:
            text = self.translations[self.current_language].get(key, key)
            return text.format(**kwargs) if kwargs else text
        except Exception:
            return key

class YTDLPApp:
    def __init__(self, master):
        self.master = master
        self.translator = Translator()

        master.title(self.translator.translate('app_title'))
        master.geometry("600x550")

        # 语言选择
        self.language_frame = tk.Frame(master)
        self.language_frame.pack(pady=(10, 0))
        
        self.language_label = tk.Label(self.language_frame, text="Language / 语言:")
        self.language_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.language_var = tk.StringVar(value=self.translator.current_language)
        self.language_options = list(self.translator.get_available_languages().keys())
        self.language_dropdown = ttk.Combobox(self.language_frame, textvariable=self.language_var, values=self.language_options, width=10)
        self.language_dropdown.pack(side=tk.LEFT)
        self.language_dropdown.bind('<<ComboboxSelected>>', self.change_language)

        # URL输入区域
        self.url_label = tk.Label(master, text=self.translator.translate('url_label'))
        self.url_label.pack(pady=(10, 0))
        
        self.url_text = tk.Text(master, height=6, width=70)
        self.url_text.pack(pady=10)

        # 质量选择
        self.quality_frame = tk.Frame(master)
        self.quality_frame.pack(pady=10)
        
        self.quality_label = tk.Label(self.quality_frame, text=self.translator.translate('quality_label'))
        self.quality_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.quality_var = tk.StringVar(value="best")
        self.quality_options = ["best", "worst", "bestvideo", "bestaudio"]
        self.quality_dropdown = ttk.Combobox(self.quality_frame, textvariable=self.quality_var, values=self.quality_options, width=20)
        self.quality_dropdown.pack(side=tk.LEFT)

        # 输出目录选择
        self.output_frame = tk.Frame(master)
        self.output_frame.pack(pady=10)
        
        self.output_label = tk.Label(self.output_frame, text=self.translator.translate('output_label'))
        self.output_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.output_entry = tk.Entry(self.output_frame, textvariable=self.output_path, width=40)
        self.output_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.browse_button = tk.Button(self.output_frame, text=self.translator.translate('browse_button'), command=self.browse_output_dir)
        self.browse_button.pack(side=tk.LEFT)

        # 下载按钮
        self.download_button = tk.Button(master, text=self.translator.translate('download_button'), command=self.start_download)
        self.download_button.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(master, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)

        # 状态标签
        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

    def change_language(self, event=None):
        selected_language = self.language_var.get()
        self.translator.set_language(selected_language)
        self.update_ui_language()

    def update_ui_language(self):
        self.master.title(self.translator.translate('app_title'))
        self.url_label.config(text=self.translator.translate('url_label'))
        self.quality_label.config(text=self.translator.translate('quality_label'))
        self.output_label.config(text=self.translator.translate('output_label'))
        self.browse_button.config(text=self.translator.translate('browse_button'))
        self.download_button.config(text=self.translator.translate('download_button'))

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)

    def start_download(self):
        urls = self.url_text.get("1.0", tk.END).strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]

        if not urls:
            messagebox.showerror("Error", self.translator.translate('error_no_url'))
            return

        quality = self.quality_var.get()
        output_dir = self.output_path.get()

        # 禁用下载按钮防止重复点击
        self.download_button.config(state=tk.DISABLED)
        self.progress["value"] = 0

        # 使用线程防止GUI冻结
        threading.Thread(target=self.download_videos, args=(urls, quality, output_dir), daemon=True).start()

    def download_videos(self, urls, quality, output_dir):
        try:
            for i, url in enumerate(urls, 1):
                self.update_status(self.translator.translate('status_downloading', current=i, total=len(urls), url=url))
                
                ydl_opts = {
                    'format': quality,
                    'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 更新进度条
                self.progress["value"] = int((i / len(urls)) * 100)
                self.master.update_idletasks()

            self.update_status(self.translator.translate('status_download_finished'))
        except Exception as e:
            self.update_status(self.translator.translate('status_download_error', error=str(e)))
        finally:
            self.master.after(0, self.reset_download_button)

    def progress_hook(self, d):
        if d['status'] == 'finished':
            self.update_status(self.translator.translate('status_converting'))

    def update_status(self, message):
        self.master.after(0, lambda: self.status_label.config(text=message))

    def reset_download_button(self):
        self.download_button.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = YTDLPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
