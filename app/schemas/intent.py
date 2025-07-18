from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class IntentRequest(BaseModel):
    """意图识别请求模型"""
    text: str = Field(..., description="用户输入的文本", min_length=1, max_length=1000)
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "我想查询今天的天气",
                "user_id": "user123",
                "session_id": "session456"
            }
        }

class IntentConfidence(BaseModel):
    """意图置信度模型"""
    intent: str = Field(..., description="意图类型")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "intent": "weather_query",
                "confidence": 0.95
            }
        }

class IntentResponse(BaseModel):
    """意图识别响应模型"""
    text: str = Field(..., description="原始输入文本")
    intent: str = Field(..., description="识别出的主要意图")
    confidence: float = Field(..., description="主要意图的置信度", ge=0.0, le=1.0)
    all_intents: List[IntentConfidence] = Field(..., description="所有可能的意图及其置信度")
    entities: Optional[dict] = Field(None, description="提取的实体信息")
    processing_time: float = Field(..., description="处理时间（毫秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="处理时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "我想查询今天的天气",
                "intent": "weather_query",
                "confidence": 0.95,
                "all_intents": [
                    {"intent": "weather_query", "confidence": 0.95},
                    {"intent": "general_query", "confidence": 0.03},
                    {"intent": "unknown", "confidence": 0.02}
                ],
                "entities": {
                    "time": "今天",
                    "query_type": "天气"
                },
                "processing_time": 150.5,
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class IntentTrainingData(BaseModel):
    """意图训练数据模型"""
    text: str = Field(..., description="训练文本")
    intent: str = Field(..., description="对应的意图标签")
    confidence: Optional[float] = Field(None, description="人工标注的置信度")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "今天天气怎么样",
                "intent": "weather_query",
                "confidence": 1.0
            }
        }

class IntentModelInfo(BaseModel):
    """意图模型信息模型"""
    model_name: str = Field(..., description="模型名称")
    version: str = Field(..., description="模型版本")
    accuracy: float = Field(..., description="模型准确率")
    training_samples: int = Field(..., description="训练样本数量")
    last_updated: datetime = Field(..., description="最后更新时间")
    
    class Config:
        schema_extra = {
            "example": {
                "model_name": "intent_classifier_v1",
                "version": "1.0.0",
                "accuracy": 0.92,
                "training_samples": 10000,
                "last_updated": "2024-01-01T12:00:00"
            }
        }

class IntentDetectionRequest(BaseModel):
    """意图检测请求模型"""
    query: str = Field(..., description="用户查询文本", min_length=1, max_length=1000)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "富集分析"
            }
        }

class IntentDetectionResponse(BaseModel):
    """意图检测响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    intent: int = Field(..., description="意图分类结果：1表示生信分析相关，0表示不相关，2表示高级生信分析")
    is_bioinformatics_related: bool = Field(..., description="是否与生物信息学相关")
    
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "Success",
                "intent": 1,
                "is_bioinformatics_related": True
            }
        } 