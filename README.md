# YT-DLP GUI 下载器

## 功能特点
- 支持视频批量下载
- 可选择下载质量
- 简单易用的图形界面

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行
```bash
python main.py
```

## 构建说明

### 使用 PyInstaller 打包

1. 单文件模式：
```bash
pyinstaller --onefile main.py
```

2. 多文件模式：
```bash
pyinstaller ytdlp_gui.spec
```

### 手动构建

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行应用
```bash
python main.py
```

# 许可
本项目遵循 [MIT 许可协议](LICENSE)


# 致谢

本项目使用了下列开源项目:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
