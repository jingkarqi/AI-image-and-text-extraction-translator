# 图片题目处理系统

本项目实现从图片中提取题目并自动翻译的功能，主要包含两个处理阶段：
1. 图片文字提取（pic-response.py）
2. 题目翻译（translator.py）

## 功能特点
- 支持多种图片格式：PNG/JPG/JPEG/BMP/WEBP
- 自动保存处理结果到JSON文件
- 中英文题目自动翻译

## 环境要求
- Python 3.11+
- 依赖安装：
```bash
pip install -r requirements.txt
```
- 需在`config.py`中配置API密钥

## 使用说明

### 1. 图片处理阶段
```bash
python pic-response.py "input_image文件路径" --output_dir "json_result文件路径"
```
参数说明：
- `input_dir`: 输入图片目录路径（必须）
- `--output_dir`: 输出目录路径（默认：./json-result）

### 2. 翻译阶段
```bash
python translator.py
```
自动处理json-result目录下的所有文件，翻译结果保存到translated-result目录

## 项目结构
```
GITS/
├── input_images/        # 原始图片目录
├── json-result/         # 图片处理结果
├── translated-result/   # 翻译结果
├── config.py            # API配置
├── pic-response.py      # 图片处理主程序
├── translator.py        # 翻译程序
└── qwen_vl_extractor.py # 图片处理核心模块
```

## 注意事项
1. 请确保输入图片文件名规范（如示例中的b (1).png格式）
2. API密钥需要自行申请并配置到config.py
3. 输出目录会自动创建，无需手动创建
```

