from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.query_graph import get_possible_pipeline
from app.utils.replace_tools import replace_tools
from pydantic import BaseModel
from typing import Dict, Any, Optional, List


router = APIRouter()
logger = get_logger(__name__)


class PipelineRequest(BaseModel):
    tool_names: List[str]
    preloading: List[str]
    project: str


class PipelineResponse(BaseModel):
    code: int
    message: str
    result: Optional[Dict[str, Any]] = None


class ReplacetoolsRequest(BaseModel):
    workflow_id: str

@router.post("/get_possible_pipeline", response_model=PipelineResponse)
async def get_possible_pipeline_endpoint(request: PipelineRequest):
    """
    获取可行流水线接口
    基于 `tool_names`、`preloading`、`project` 调用 `get_possible_pipeline`。
    """
    logger.info("收到可行流水线查询请求")

    try:
        result = replace_tools(
            tool_names=request.tool_names,
            preloading=request.preloading,
            project=request.project,
        )
        print(result["possible_pipeline"])
        rrr={"pipeline":result["possible_pipeline"],"long_pipeline":len(result["possible_pipeline"])}
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="查询结果异常")

        return PipelineResponse(
            code=200,
            message="Success",
            result=rrr,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"可行流水线查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/reolace_tools", response_model=PipelineResponse)
async def reolace_tools_endpoint(request: ReplacetoolsRequest):
    """
    获取可行流水线接口
    基于 `workflow_id` 调用 更多的`workflow_id`。
    """
    logger.info("收到可行流水线查询请求")

    try:
        result = replace_tools(
            request.workflow_id,
        )
        print(result)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="查询结果异常")

        return PipelineResponse(
            code=200,
            message="Success",
            result=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"可行流水线查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

