"""
pic-response.py: 主程序脚本，用于处理图片目录并提取问题。

This script serves as the main entry point for processing a directory of images
and extracting questions using the QwenVLExtractor.

Functions:
    main: 主程序入口，处理命令行参数并执行图片处理流程。
"""

import argparse
import logging
from pathlib import Path

from qwen_vl_extractor import QwenVLExtractor
from config import VLLM_API_KEY

def main() -> None:
    """
    图片处理主程序

    功能：
    1. 从命令行接收输入目录和输出目录参数
    2. 初始化QwenVLExtractor提取器
    3. 处理指定目录中的所有图片

    异常：
    当发生以下情况时抛出异常：
    - 输入目录不存在
    - API配置错误
    - 图片处理失败
    """
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('processing.log'), logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='图片题目提取处理器')
    parser.add_argument('input_dir', type=str, help='输入图片目录路径')
    parser.add_argument('--output_dir', 
                        type=str, 
                        default='json-result',
                        help='输出目录路径（默认：./json-result）')
    args = parser.parse_args()

    try:
        input_path = Path(args.input_dir)
        output_path = Path(args.output_dir)

        # 确保输入目录存在
        if not input_path.is_dir():
            raise NotADirectoryError(f"输入目录不存在或不是一个目录: {args.input_dir}")

        # 初始化提取器
        extractor = QwenVLExtractor(api_key=VLLM_API_KEY)
        
        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f'开始处理目录：{args.input_dir}')
        extractor.process_directory(input_path, output_path)
        
        # 计算处理的图片数量
        processed_images = len([f for f in input_path.glob('*') if f.suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}])
        logger.info(f'成功处理 {processed_images} 张图片')
    
    except NotADirectoryError as e:
        logger.error(f"目录错误: {str(e)}")
        raise
    except PermissionError as e:
        logger.error(f"权限错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f'处理过程中发生错误：{str(e)}', exc_info=True)
        raise

if __name__ == '__main__':
    main()
