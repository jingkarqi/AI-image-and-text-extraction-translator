"""
QwenVLExtractor: 使用Qwen VL模型从图片中提取问题和选项

本模块提供基于Qwen VL（视觉-语言）模型的图片题目提取功能，支持处理单个图片或整个目录的图片。

类:
    QwenVLExtractor: 图片处理和文本提取的主类

函数:
    main: QwenVLExtractor的示例用法
"""

import base64
import json
import logging
from pathlib import Path
from typing import Dict, Union
from config import VLLM_API_KEY, VLLM_BASE_URL, VLLM_MODEL_ID  # 添加 VLLM_MODEL_ID 导入
from openai import OpenAI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QwenVLExtractor:
    """
    基于Qwen VL模型的图片题目提取类

    属性:
        client (OpenAI): 用于API调用的OpenAI客户端
        model_name (str): 使用的Qwen VL模型名称
    """

    def __init__(self, api_key: str = None, model_name: str = None):  # 修改默认值为None
        """
        初始化QwenVLExtractor

        参数:
            api_key (str, 可选): DashScope API密钥。如果未提供，将从config获取
            model_name (str, 可选): 使用的Qwen VL模型名称，默认为"qwen2-vl-72b-instruct"
        """
        from config import VLLM_API_KEY, VLLM_BASE_URL, VLLM_MODEL_ID  # 添加完整导入

        self.api_key = api_key or VLLM_API_KEY
        if not self.api_key:
            raise ValueError("API key not set. Please set VLLM_API_KEY in config.py or provide it during initialization.")

        self.client = OpenAI(api_key=self.api_key, base_url=VLLM_BASE_URL)
        self.model_name = model_name or VLLM_MODEL_ID  # 修改为安全赋值方式

    @staticmethod
    def encode_image(image_path: Union[str, Path]) -> str:
        """
        将图片编码为base64格式

        参数:
            image_path (Union[str, Path]): 图片文件路径

        返回:
            str: Base64编码的图片数据
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_questions(self, image_path: Union[str, Path]) -> Dict:
        """
        从图片中提取题目和选项

        参数:
            image_path (Union[str, Path]): 图片文件路径

        返回:
            Dict: 包含提取结果的字典

        异常:
            Exception: API调用失败时抛出
        """
        base64_image = self.encode_image(image_path)
        
        system_prompt = "You are a professional question extractor. Please extract questions and options from the image. Use markdown format for tables and JSON format for other cases."
        user_prompt = "Please extract all questions and options from this image, ensuring completeness and accuracy."

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                        {"type": "text", "text": user_prompt}
                    ]}
                ]
            )
            
            return self._parse_response(completion.choices[0].message.content)
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise

    @staticmethod
    def _parse_response(response: str) -> Dict:
        """
        Parse the API response.

        Args:
            response (str): API response text.

        Returns:
            Dict: Parsed data dictionary.
        """
        if "|" in response and "-|-" in response:
            return {"type": "markdown", "content": response}
        
        try:
            return {"type": "json", "content": json.loads(response)}
        except json.JSONDecodeError:
            return {"type": "text", "content": response}

    def process_image(self, image_path: Union[str, Path], output_dir: Union[str, Path]) -> None:
        """
        Process a single image and save the result.

        Args:
            image_path (Union[str, Path]): Path to the image file.
            output_dir (Union[str, Path]): Directory to save the output JSON file.
        """
        try:
            image_path = Path(image_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            result = self.extract_questions(image_path)
            
            output_path = output_dir / f"{image_path.stem}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Successfully processed image {image_path} and saved result to {output_path}")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")

    def process_directory(self, directory: Union[str, Path], output_dir: Union[str, Path]) -> None:
        """
        Process all images in a directory.

        Args:
            directory (Union[str, Path]): Path to the directory containing images.
            output_dir (Union[str, Path]): Directory to save the output JSON files.
        """
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        directory_path = Path(directory)
        
        for image_path in directory_path.glob("*"):
            if image_path.suffix.lower() in image_extensions:
                self.process_image(image_path, output_dir)

def main():
    """Example usage of the QwenVLExtractor class."""
    extractor = QwenVLExtractor()
    
    # Process a single image
    # extractor.process_image("path/to/image.png", "path/to/output/directory")
    
    # Process all images in a directory
    # extractor.process_directory("path/to/image/directory", "path/to/output/directory")

if __name__ == "__main__":
    main()