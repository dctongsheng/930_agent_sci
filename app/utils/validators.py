import re
from typing import Any, Dict, List
from app.core.logging import get_logger

logger = get_logger(__name__)

class DataValidator:
    """数据验证工具类"""
    
    def __init__(self):
        """初始化验证器"""
        # 定义正则表达式
        self.patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone": r'^1[3-9]\d{9}$',
            "user_id": r'^[a-zA-Z0-9_-]{3,20}$',
            "session_id": r'^[a-zA-Z0-9_-]{10,50}$'
        }
        
        logger.info("数据验证器初始化完成")
    
    def validate_text(self, text: str, min_length: int = 1, max_length: int = 1000) -> Dict[str, Any]:
        """
        验证文本数据
        
        Args:
            text: 输入文本
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        # 检查是否为空
        if not text or not text.strip():
            result["is_valid"] = False
            result["errors"].append("文本不能为空")
        
        # 检查长度
        if len(text) < min_length:
            result["is_valid"] = False
            result["errors"].append(f"文本长度不能少于{min_length}个字符")
        
        if len(text) > max_length:
            result["is_valid"] = False
            result["errors"].append(f"文本长度不能超过{max_length}个字符")
        
        # 检查是否包含恶意内容（简单检查）
        malicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'<iframe.*?>.*?</iframe>',
            r'<object.*?>.*?</object>'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result["is_valid"] = False
                result["errors"].append("文本包含不允许的内容")
                break
        
        return result
    
    def validate_user_id(self, user_id: str) -> Dict[str, Any]:
        """
        验证用户ID
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if user_id and not re.match(self.patterns["user_id"], user_id):
            result["is_valid"] = False
            result["errors"].append("用户ID格式不正确")
        
        return result
    
    def validate_session_id(self, session_id: str) -> Dict[str, Any]:
        """
        验证会话ID
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if session_id and not re.match(self.patterns["session_id"], session_id):
            result["is_valid"] = False
            result["errors"].append("会话ID格式不正确")
        
        return result
    
    def validate_intent_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证意图识别请求数据
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        # 验证必需字段
        required_fields = ["text"]
        for field in required_fields:
            if field not in data or not data[field]:
                result["is_valid"] = False
                result["errors"].append(f"缺少必需字段: {field}")
        
        # 验证文本
        if "text" in data:
            text_validation = self.validate_text(data["text"])
            if not text_validation["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(text_validation["errors"])
        
        # 验证可选字段
        if "user_id" in data and data["user_id"]:
            user_id_validation = self.validate_user_id(data["user_id"])
            if not user_id_validation["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(user_id_validation["errors"])
        
        if "session_id" in data and data["session_id"]:
            session_id_validation = self.validate_session_id(data["session_id"])
            if not session_id_validation["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(session_id_validation["errors"])
        
        return result
    
    def sanitize_text(self, text: str) -> str:
        """
        清理文本，移除潜在的危险内容
        
        Args:
            text: 输入文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除JavaScript代码
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # 移除SQL注入相关字符
        sql_patterns = [
            r'(\b)(union|select|insert|update|delete|drop|create|alter)(\b)',
            r'(\b)(or|and)(\s+)(\d+)(\s*)(=)(\s*)(\d+)',
            r'(\b)(or|and)(\s+)(\w+)(\s*)(=)(\s*)(\w+)'
        ]
        
        for pattern in sql_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def validate_batch_request(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证批量请求数据
        
        Args:
            requests: 请求列表
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        # 检查请求列表是否为空
        if not requests:
            result["is_valid"] = False
            result["errors"].append("请求列表不能为空")
            return result
        
        # 检查请求数量限制
        if len(requests) > 100:  # 最多100个请求
            result["is_valid"] = False
            result["errors"].append("批量请求数量不能超过100个")
        
        # 验证每个请求
        for i, request in enumerate(requests):
            request_validation = self.validate_intent_request(request)
            if not request_validation["is_valid"]:
                result["is_valid"] = False
                result["errors"].append(f"第{i+1}个请求验证失败: {'; '.join(request_validation['errors'])}")
        
        return result 