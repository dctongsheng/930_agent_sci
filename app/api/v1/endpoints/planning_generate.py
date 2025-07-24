from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.call_dify import plan_generate
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

router = APIRouter()
logger = get_logger(__name__)

class PlanningGenerateRequest(BaseModel):
    data_meatinfo: Dict[str, Any]
    query: str
    omics: str

class PlanningGenerateResponse(BaseModel):
    code: int
    message: str
    planning_result: Optional[Dict[str, Any]] = None

@router.post("/planning_generate", response_model=PlanningGenerateResponse)
async def planning_generate_endpoint(request: PlanningGenerateRequest):
    """
    规划生成接口
    基于data_meatinfo和query生成规划
    """
    logger.info(f"收到规划生成请求: {request.query}")
    data_choose=request.data_meatinfo

    print(request.omics)



    if request.omics != "":
        res_l=[]
        for i in data_choose["records"]:
                
            # if i["dataType"]==0:
                i["omicsType"]=request.omics
                print(i["omicsType"])
                res_l.append(i)
        data_choose["records"]=res_l

            # print(data_choose["record"]["omicsType"])

    try:
        # 调用规划生成函数
        planning_result = await plan_generate(
            data_choose=json.dumps(data_choose),
            query=request.query
        )
        fff={}
        fff["structured_output"]={"planning_steps":planning_result}
        print(fff)
        
        return PlanningGenerateResponse(
            code=200,
            message="Success",
            planning_result=fff
        )
    except Exception as e:
        logger.error(f"规划生成失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
