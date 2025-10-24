from fastapi import APIRouter, HTTPException
from app.core.logging import get_logger
from app.utils.call_dify import multi_chat_with_api
from app.utils.call_dify import pipline_generate,multi_chat_agent
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
from app.utils.query_graph import get_possible_pipeline
from app.utils.search_tools_by_id import query_workflow_id


router = APIRouter()
logger = get_logger(__name__)

class MultiChatRequest(BaseModel):
    data_choose: Dict[str, Any]
    query_template: str
    conversation_id: str    
    xtoken: str
    state: int=1

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
    need_plan=False

    # print(request.input)
    
    try:
        # 调用图像推荐函数
        if not need_plan:
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
                planning_result={"mul_chat":False,"key_text":"直接调用planning生成"}
            )         
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像推荐失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/pipline_generate", response_model=MultiChatResponse)
async def pipline_generate_endpoint(request: MultiChatRequest):
    """
    生成pipline接口
    """
    logger.info(f"收到生成pipline请求")
    data_choose=request.data_choose
    query_template=request.query_template
    conversation_id=request.conversation_id
    xtoken=request.xtoken
    state=request.state
    try:
        planning_result = await pipline_generate(json.dumps(data_choose),query_template,conversation_id,xtoken,state)
        logger.info(f"planning_result: {planning_result}")
        print(planning_result)

        if planning_result["mul_chat"]:
            return MultiChatResponse(
                code=200,
                message="Success",
                planning_result=planning_result
            )
        else:
            try:
                if planning_result["lastnode"] is not None and planning_result["lastnode"] != [] and any(node.strip() for node in planning_result["lastnode"]):
                    print(planning_result["lastnode"][0])
                    planning_result_pipeline = get_possible_pipeline(planning_result["lastnode"],planning_result["preloading"],planning_result["projectid"])
                    print(planning_result_pipeline)
                    result001=query_workflow_id(planning_result_pipeline["possible_pipeline"][0])
                    print(result001)
                    planning_result["pipleline"]=result001
                else:
                    planning_result["pipleline"]=["没有找到可用的pipline"]
            except Exception as e:
                logger.error(f"生成pipline失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal server error: {str(e)}"
                )
        
        if planning_result is None:
            raise HTTPException(
                status_code=500,
                detail="生成pipline失败"
            )
        return MultiChatResponse(
            code=200,
            message="Success",
            planning_result=planning_result
        )
    except Exception as e:
        logger.error(f"生成pipline失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/multi_chat_agent_prd", response_model=MultiChatResponse)
async def multi_chat_agent_endpoint(request: MultiChatRequest):
    """
    生成pipline接口
    """
    logger.info(f"收到生成pipline请求")
    data_choose=request.data_choose
    query_template=request.query_template
    conversation_id=request.conversation_id
    # need_plan=request.need_plan
    xtoken=request.xtoken
    state=request.state
    # need_plan=True
    print(query_template)
    try:
        planning_result = await multi_chat_agent(json.dumps(data_choose),query_template,conversation_id,xtoken,state)
        logger.info(f"planning_result: {planning_result}")
        print(planning_result)

        if planning_result["mul_chat"]:
            return MultiChatResponse(
                code=200,
                message="Success",
                planning_result=planning_result
            )
        else:
            try:
                if planning_result["lastnode"] is not None and planning_result["lastnode"] != [] and any(node.strip() for node in planning_result["lastnode"]):
                    print(planning_result["lastnode"][0])
                    planning_result_pipeline = get_possible_pipeline(planning_result["lastnode"],planning_result["preloading"],planning_result["projectid"])
                    print(planning_result_pipeline)
                    try:
                        result001=query_workflow_id(planning_result_pipeline["possible_pipeline"][0])
                        print(result001)
                        planning_result["planning_steps"]=result001
                        planning_result["text"]="已经根据你的需求为你生成的pipleline如下："
                    except Exception as e:
                        planning_result["text"]="对不起，您选择的数据和分析任务不符合"
                        planning_result["mul_chat"]=False
                        # planning_result["planning_steps"]={
                        #             "text": "对不起，您选择的数据和分析任务不符合",
                        #             "conversation_id": planning_result["conversation_id"],
                        #             "mul_chat": True}
                else:
                    planning_result["text"]="对不起，数据库中没有找到合适的app"
                    planning_result["mul_chat"]=False
                    # planning_result["planning_steps"]={
                    #                                     "text": "对不起，数据库中没有找到合适的app",
                    #                                     "conversation_id": planning_result["conversation_id"],
                    #                                     "mul_chat": True}
            except Exception as e:
                logger.error(f"生成pipline失败: {e}")
                return MultiChatResponse(
                code=400,
                message="生成pipeline流程失败",
                planning_result={"error":f"抽取工具以及任务模块调用失败：失败原因 {str(e)}"}
                )
                # raise HTTPException(
                #     status_code=500,
                #     detail=f"Internal server error: {str(e)}"
                # )
        
        if planning_result is None:
            return MultiChatResponse(
            code=400,
            message="生成pipeline失败",
            planning_result={"error":"plan生成的结果为空"}
            )
            # raise HTTPException(
            #     status_code=500,
            #     detail="生成pipline失败"
            # )
        return MultiChatResponse(
            code=200,
            message="Success",
            planning_result=planning_result
        )
    except Exception as e:
        logger.error(f"生成pipline失败: {e}")
        return MultiChatResponse(
        code=400,
        message="生成pipeline失败",
        planning_result={"error":f"调用数据库失败,pre-loading结果为空：失败原因 {str(e)}"}
        )
        # raise HTTPException(
        #     status_code=500,
        #     detail=f"调用数据库失败L：失败原因 {str(e)}"
        # )

@router.post("/multi_chat_agent_test", response_model=MultiChatResponse)
async def multi_chat_agent_endpoint(request: MultiChatRequest):
    """
    生成pipline接口
    """
    logger.info(f"收到生成pipline请求")
    data_choose=request.data_choose
    query_template=request.query_template
    conversation_id=request.conversation_id
    # need_plan=request.need_plan
    xtoken=request.xtoken
    state=request.state
    # need_plan=True
    print(query_template)
    try:
        planning_result = await pipline_generate(json.dumps(data_choose),query_template,conversation_id,xtoken,state)
        logger.info(f"planning_result: {planning_result}")
        print(planning_result)

        if planning_result["mul_chat"]:
            return MultiChatResponse(
                code=200,
                message="Success",
                planning_result=planning_result
            )
        else:
            try:
                if planning_result["lastnode"] is not None and planning_result["lastnode"] != [] and any(node.strip() for node in planning_result["lastnode"]):
                    print(planning_result["lastnode"][0])
                    planning_result_pipeline = get_possible_pipeline(planning_result["lastnode"],planning_result["preloading"],planning_result["projectid"])
                    print(planning_result_pipeline)
                    try:
                        result001=query_workflow_id(planning_result_pipeline["possible_pipeline"][0])
                        print(result001)
                        planning_result["planning_steps"]=result001
                        planning_result["text"]="已经根据你的需求为你生成的pipleline如下："
                    except Exception as e:
                        planning_result["planning_steps"]={
                                    "text": "对不起，数据库中没有找到合适的app",
                                    "conversation_id": planning_result["conversation_id"],
                                    "mul_chat": True}
                else:
                    planning_result["planning_steps"]={
                                                        "text": "对不起，数据库中没有找到合适的app",
                                                        "conversation_id": planning_result["conversation_id"],
                                                        "mul_chat": True}
            except Exception as e:
                logger.error(f"生成pipline失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal server error: {str(e)}"
                )
        
        if planning_result is None:
            raise HTTPException(
                status_code=500,
                detail="生成pipline失败"
            )
        return MultiChatResponse(
            code=200,
            message="Success",
            planning_result=planning_result
        )
    except Exception as e:
        logger.error(f"生成pipline失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )