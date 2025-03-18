from openai import OpenAI
import os
import json
from pathlib import Path

# 导入配置
from config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL_ID

# 配置API
client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)

# 翻译系统提示
SYSTEM_PROMPT = """
你是一个专业的翻译助手，请将输入的英文文本翻译成中文。翻译时请注意：
1. 保持专业术语的准确性
2. 保留所有代码块和SQL语句不翻译
3. 保持文本的格式和结构
4. 保持原有表达意义
"""

def translate_text(text):
    """
调用大模型API进行文本翻译

参数:
    text (str): 需要翻译的英文文本

返回:
    str: 翻译后的中文文本
"""
    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL_ID,  # 使用配置中的模型ID
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"翻译出错: {e}")
        return None

def process_json_file(input_file, output_dir):
    """
处理单个JSON文件

参数:
    input_file (str): 输入文件路径
    output_dir (str): 输出目录路径

异常:
    Exception: 文件处理失败时抛出
"""
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取文本内容
        text = data.get('content', '')  # 修改为 content 字段
        if not text:
            print(f"文件 {input_file} 中没有找到content字段")
            return
        
        # 翻译文本
        translated_text = translate_text(text)
        if translated_text is None:
            return
        
        # 构建输出文件路径
        output_file = Path(output_dir) / f"translated_{Path(input_file).name}"
        
        # 保存翻译结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"content": translated_text}, f, ensure_ascii=False, indent=2)  # 修改为 content 字段
            
        print(f"已完成文件 {input_file} 的翻译")
        
    except Exception as e:
        print(f"处理文件 {input_file} 时出错: {e}")

def main():
    # 设置输入输出目录
    input_dir = Path("json-result")
    output_dir = Path("translated-result")
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 处理所有JSON文件
    for json_file in input_dir.glob("*.json"):
        process_json_file(json_file, output_dir)

if __name__ == "__main__":
    main()