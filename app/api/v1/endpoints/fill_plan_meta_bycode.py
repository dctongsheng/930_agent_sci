from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.run_workflow import fill_meta_by_code,description_ai_auto_fill_v2
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()
logger = get_logger(__name__)

class RecommendImagesRequest(BaseModel):
    input: Dict[str, Any]

class RecommendImagesResponse(BaseModel):
    code: int
    message: str
    recommend_result: Optional[Dict[str, Any]] = None

@router.post("/fill_plan_meta_bycode", response_model=RecommendImagesResponse)
async def recommend_images_endpoint(request: RecommendImagesRequest):
    """
    图像推荐接口
    基于查询条件推荐相关图像
    """
    logger.info(f"收到基于code填写meta的请求")

    # print(request.input)
    
    try:
        # 调用图像推荐函数
        recommend_result = await fill_meta_by_code(request.input)
        
        if recommend_result is None:
            raise HTTPException(
                status_code=500,
                detail="图像推荐失败"
            )
        
        return RecommendImagesResponse(
            code=200,
            message="Success",
            recommend_result=recommend_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像推荐失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/description_ai_auto", response_model=RecommendImagesResponse)
async def des_autofill_endpoint(request: RecommendImagesRequest):
    """
    图像推荐接口
    基于查询条件推荐相关图像
    """
    logger.info(f"收到基于code填写meta的请求")

    # print(request.input)
    
    try:
        # 调用图像推荐函数
        recommend_result = await description_ai_auto_fill_v2(request.input)
        
        if recommend_result is None:
            raise HTTPException(
                status_code=500,
                detail="图像推荐失败"
            )
        
        return RecommendImagesResponse(
            code=200,
            message="Success",
            recommend_result=recommend_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像推荐失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )