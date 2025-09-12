from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.call_dify import multi_chat_with_api
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
router = APIRouter()
logger = get_logger(__name__)

class MultiChatRequest(BaseModel):
    data_choose: Dict[str, Any]
    query_template: str
    conversation_id: str
    need_plan: int

class MultiChatResponse(BaseModel):
    code: int
    message: str
    planning_result: Optional[Dict[str, Any]] = None

@router.post("/multi_chat_data_choose", response_model=MultiChatResponse)
async def multi_chat_endpoint(request: MultiChatRequest):
    """
    图像推荐接口
    基于查询条件推荐相关图像
    """
    logger.info(f"收到多轮对话请求")
    data_choose=request.data_choose
    query_template=request.query_template
    conversation_id=request.conversation_id
    need_plan=request.need_plan

    # print(request.input)
    
    try:
        # 调用图像推荐函数
        if need_plan==0:
            planning_result = await multi_chat_with_api(json.dumps(data_choose),query_template,conversation_id)
            
            if planning_result is None:
                raise HTTPException(
                    status_code=500,
                    detail="图像推荐失败"
                )
            
            return MultiChatResponse(
                code=200,
                message="Success",
                planning_result=planning_result
            )
        else:
            return MultiChatResponse(
                code=200,
                message="Success",
                planning_result={"need_plan":1,"key_text":"直接调用planning生成"}
            )         
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像推荐失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
