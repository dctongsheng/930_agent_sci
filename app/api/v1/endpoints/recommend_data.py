from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.run_workflow import recommend_data
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

router = APIRouter()
logger = get_logger(__name__)

import time

# 生成当前时间戳（秒级整数）
timestamp = int(time.time())

class RecommendDataRequest(BaseModel):
    input: Dict[str, Any]

class RecommendDataResponse(BaseModel):
    code: int
    message: str
    recommend_result: Optional[Dict[str, Any]] = None

def extract_suffix(filename):
    """
    提取文件后缀，特别处理.gef结尾的文件
    
    Args:
        filename (str): 文件名
        
    Returns:
        str: 后缀类型
    """
    if filename.endswith('.gef'):
        if filename.endswith('tissue.gef'):
            return 'tissue.gef'
        elif filename.endswith('cellbin.gef'):
            return 'cellbin.gef'
        else:
            return 'gef'
    else:
        # 返回其他后缀
        return filename.split('.')[-1] if '.' in filename else ''

def extra_previous_step(previous_step,title):
    if len(previous_step)>0 and "细胞注释" in previous_step:
        return "细胞注释"
    elif len(previous_step)==1: 
        return previous_step[0]
    elif len(previous_step)==0:
            return title
    else:
        return title
dic_p={
"STOmics": {
  "数据预处理": "Y00862D8.tissue.gef",
  "数据质控分析": "Y00862D8.tissue.gef",
  "细胞聚类分析": "Y00862D8_pre_anndata.h5ad",
  "细胞注释": "Y00862D8.bin50_1.0.h5ad"
},
"scRNA_seq": {
  "数据预处理": "tetssc123_scRNA_dataqc.h5ad",
  "数据质控分析": "filter_matrix",
  "细胞聚类分析": "demo_scRNA_cluster_anndata.h5ad",
  "细胞注释": "demo_scRNA_cluster_anndata.h5ad"
}
}

async def main_re_data(plan: dict,data_name:str,omics:str) -> dict:

    try:
        # 将字符串转换为字典
        result_dict = plan
        step_num = int(result_dict["step"])
        houzui = extract_suffix(data_name)
        previous_step=extra_previous_step(result_dict["previous_step"],result_dict["title"])

        image_contain_name = result_dict["title"]+"_"+result_dict["tools"]+"_"+str(timestamp)
        # print(previous_step)
        pipei_dict = dic_p[omics]
        if step_num==1:
            if houzui=="gef":
                fff="Y00862D8.gef"
            elif houzui=="tissue.gef":
                fff="Y00862D8.tissue.gef"
            elif houzui=="cellbin.gef":
                fff="Y00862D8.raw.cellbin.gef"
            elif houzui=="h5ad":
                try:
                    fff=pipei_dict[previous_step]
                except Exception as e:
                    fff=""
        else:
            print(previous_step)

            try:
                fff=pipei_dict[previous_step]
            except Exception as e:
                    fff=""

        if fff:
            result_dict["demo_input_params"]={"input":"/home/stereonote/model/Script_demo_data/"+fff}
        else:
            result_dict["demo_input_params"]={"input":fff}
        result_dict["demo_output_params"]={"output":"/data/work"}
        result_dict["image_contain_name"]=image_contain_name
        return {
            "result": result_dict,
        }
    except json.JSONDecodeError:
        return {"result":{"error": "输入的字符串不是有效的 JSON 格式"}}

@router.post("/recommend_data_", response_model=RecommendDataResponse)
async def recommend_images_endpoint(request: RecommendDataRequest):
    """
    图像推荐接口
    基于查询条件推荐相关图像
    """
    logger.info(f"收到图像推荐请求")

    # print(request.input)
    
    try:
        # 调用图像推荐函数
        recommend_result = await recommend_data(request.input)
        
        if recommend_result is None:
            raise HTTPException(
                status_code=500,
                detail="图像推荐失败"
            )
        
        return RecommendDataResponse(
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


@router.post("/recommend_data", response_model=RecommendDataResponse)
async def recommend_images_endpoint(request: RecommendDataRequest):
    """
    图像推荐接口
    基于查询条件推荐相关图像
    """
    logger.info(f"收到图像推荐请求")

    # print(request.input)
    res=request.input
    
    try:
        # 调用图像推荐函数
        recommend_result = await main_re_data(res["plan_step"],res["data_name"],res["omics"])
        
        if recommend_result is None:
            raise HTTPException(
                status_code=500,
                detail="图像推荐失败"
            )
        
        return RecommendDataResponse(
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