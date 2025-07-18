import re
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

class TextProcessor:
    """文本处理工具类"""
    
    def __init__(self):
        """初始化文本处理器"""
        # 定义停用词
        self.stop_words = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"
        }
        
        # 定义标点符号
        self.punctuation = "，。！？；：""''（）【】《》、"
        
        logger.info("文本处理器初始化完成")
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 转换为小写
        text = text.lower()
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除标点符号
        for punct in self.punctuation:
            text = text.replace(punct, ' ')
        
        # 移除英文标点
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 再次清理空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.debug(f"文本清理: '{text}'")
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        分词（简单实现）
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 分词结果
        """
        # 简单的按空格分词
        tokens = text.split()
        
        # 移除停用词
        tokens = [token for token in tokens if token not in self.stop_words]
        
        logger.debug(f"分词结果: {tokens}")
        return tokens
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        提取关键词（伪代码）
        
        Args:
            text: 输入文本
            top_k: 返回关键词数量
            
        Returns:
            List[str]: 关键词列表
        """
        # 伪代码：关键词提取
        # 1. 分词
        tokens = self.tokenize(text)
        
        # 2. 计算词频
        word_freq = {}
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
        
        # 3. 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 4. 返回top_k个关键词
        keywords = [word for word, freq in sorted_words[:top_k]]
        
        logger.debug(f"提取关键词: {keywords}")
        return keywords
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        提取文本特征
        
        Args:
            text: 输入文本
            
        Returns:
            Dict[str, Any]: 特征字典
        """
        features = {}
        
        # 基础特征
        features["length"] = len(text)
        features["word_count"] = len(text.split())
        features["char_count"] = len(text.replace(" ", ""))
        
        # 语言学特征
        features["has_question"] = "?" in text or "？" in text
        features["has_exclamation"] = "!" in text or "！" in text
        features["has_number"] = bool(re.search(r'\d', text))
        features["has_english"] = bool(re.search(r'[a-zA-Z]', text))
        
        # 意图相关特征
        features["contains_weather_words"] = any(word in text for word in ["天气", "温度", "下雨", "晴天"])
        features["contains_time_words"] = any(word in text for word in ["时间", "几点", "现在", "今天"])
        features["contains_greeting_words"] = any(word in text for word in ["你好", "您好", "早上好"])
        features["contains_farewell_words"] = any(word in text for word in ["再见", "拜拜", "回头见"])
        features["contains_help_words"] = any(word in text for word in ["帮助", "怎么", "如何"])
        
        # 关键词
        features["keywords"] = self.extract_keywords(text)
        
        logger.debug(f"提取特征: {features}")
        return features
    
    def normalize_text(self, text: str) -> str:
        """
        文本标准化
        
        Args:
            text: 输入文本
            
        Returns:
            str: 标准化后的文本
        """
        # 统一标点符号
        text = text.replace("？", "?").replace("！", "!").replace("，", ",")
        
        # 统一空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空格
        text = text.strip()
        
        return text
    
    def is_valid_text(self, text: str) -> bool:
        """
        检查文本是否有效
        
        Args:
            text: 输入文本
            
        Returns:
            bool: 是否有效
        """
        if not text or len(text.strip()) == 0:
            return False
        
        if len(text) > 1000:  # 文本过长
            return False
        
        return True 