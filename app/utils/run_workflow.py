import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional

# from app.core.logging import get_logger

# logger = get_logger(__name__)

async def run_workflow(
  api_key: str,
  inputs: Dict[str, Any] = None,
  response_mode: str = "blocking",
  user: str = "abc-123",
  base_url: str = "http://120.76.217.102"
) -> Dict[str, Any]:
  """
  异步调用工作流API
  
  Args:
      api_key (str): API密钥
      inputs (Dict[str, Any], optional): 输入参数，默认为空字典
      response_mode (str, optional): 响应模式，默认为"blocking"
      user (str, optional): 用户标识，默认为"abc-123"
      base_url (str, optional): API基础URL
  
  Returns:
      Dict[str, Any]: API响应结果
  
  Raises:
      aiohttp.ClientError: 网络请求错误
      json.JSONDecodeError: JSON解析错误
  """
  if inputs is None:
      inputs = {}
  
  url = f"{base_url}/v1/workflows/run"
  
  headers = {
      'Authorization': f'Bearer {api_key}',
      'Content-Type': 'application/json'
  }
  
  payload = {
      "inputs": inputs,
      "response_mode": response_mode,
      "user": user
  }
  
  async with aiohttp.ClientSession() as session:
      try:
          async with session.post(
              url, 
              headers=headers, 
              json=payload,
              timeout=aiohttp.ClientTimeout(total=30)
          ) as response:
              # 检查HTTP状态码
              response.raise_for_status()
              
              # 解析JSON响应
              result = await response.json()
              return result
              
      except aiohttp.ClientError as e:
          print(f"网络请求错误: {e}")
          raise
      except json.JSONDecodeError as e:
          print(f"JSON解析错误: {e}")
          raise
      except Exception as e:
          print(f"未知错误: {e}")
          raise

# 使用示例
async def intent_detection(query:str):
  """使用示例"""
  api_key = "app-UBY1y9xj4q3dT6XV2P4uBLKi"  # 替换为实际的API密钥
  
  try:
      # 调用工作流
      result = await run_workflow(
          api_key=api_key,
          inputs={"query": query},  # 根据需要修改输入参数
          response_mode="blocking",
          user="abc-123"
      )
      print("工作流执行成功:")
      print(json.dumps(result, indent=2, ensure_ascii=False))
      try:
        if result["data"]["outputs"]["structured_output"]["classification"] == "STANDARD_BIOINFORMATICS":
            return 1
        elif result["data"]["outputs"]["structured_output"]["classification"] == "NON_BIOINFORMATICS":
            return 0
        elif result["data"]["outputs"]["structured_output"]["classification"] == "ADVANCED_BIOINFORMATICS":
            return 2
        else:
            return 0
      except Exception as e:
        print(f"工作流执行失败: {e}")
        return -1
      
  except Exception as e:
      print(f"工作流执行失败: {e}")
      return -1
  
  
async def plan_check(query:dict):
    api_key = "app-E7srcUf8TFtfrFbcFv5KhAu5"  # 替换为实际的API密钥
    json_query = json.dumps(query,ensure_ascii=False)
    try:
        result = await run_workflow(
        api_key=api_key,
        inputs={"plan_desc": json_query},
        response_mode="blocking",
        user="abc-123"
         )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")
        return -1
    return result

def stringify_dict(input_dict):
    output_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            output_dict[key] = str(stringify_dict(value))  # 递归处理字典并转换为字符串
        else:
            output_dict[key] = str(value)  # 转换为字符串
    return output_dict

def stringify_dict_2(input_dict):
    output_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            output_dict[key] = json.dumps(value,ensure_ascii=False)  # 递归处理字典并转换为字符串
        else:
            output_dict[key] = str(value)  # 转换为字符串
    return output_dict

async def recommend_images(query:dict):
    api_key = "app-WFwn3n3Ns274laHmM5OUIFtX"  # 替换为实际的API密钥
    # json_query = json.dumps(query,ensure_ascii=False)
    # print(query)
    try:
        result = await run_workflow(
            api_key=api_key,
            inputs=stringify_dict(query),
            response_mode="blocking",
            user="abc-123"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")

async def error_check(query:dict):
    api_key = "app-90QxcS86RQBjj2hM36aF25fC"  # 替换为实际的API密钥
    json_query = json.dumps(query,ensure_ascii=False)
    print(json_query)
    try:
        result = await run_workflow(
            api_key=api_key,
            inputs={"err_info": json_query},   
            response_mode="blocking",
            user="abc-123"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")
        return -1
    

    
async def data_check(query:dict):
    api_key = "app-H22BojPCUnbVgphRjbWu125X"  # 替换为实际的API密钥
    json_query = json.dumps(query,ensure_ascii=False)
    # print(json_query)
    try:
        result = await run_workflow(
            api_key=api_key,
            inputs={"data_choose": json_query},
            response_mode="blocking",
            user="abc-123"
        )
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        # print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")
        return -1

# 运行示例（如果直接执行此脚本）

async def description_ai_auto_fill(query:dict):
    api_key = "app-BQIOPjvPyGDFlwHFZiOr551K"  # 替换为实际的API密钥
    json_query = json.dumps(query,ensure_ascii=False)
    try:
        result = await run_workflow(
            api_key=api_key,
            inputs={"planning": json_query},
            response_mode="blocking",
            user="abc-123"
        )
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        # print(result["data"]["outputs"]["structured_output"]["description"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")
        return -1

async def recommend_data(query:dict):
    api_key = "app-vkRWjBRGgaFDoiWhMGN65e27"  # 替换为实际的API密钥
    # json_query = json.dumps(query,ensure_ascii=False)
    # print(query)
    try:
        res_test=stringify_dict(query)
        print(type(res_test["plan_step"]))
        print(res_test["plan_step"])
        result = await run_workflow(
            api_key=api_key,
            inputs=stringify_dict(query),
            response_mode="blocking",
            user="abc-123"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")

async def fill_params_images(query:dict):
    api_key = "app-IBCmCILzLccUm7Sq0f6lEm5B"  # 替换为实际的API密钥
    # json_query = json.dumps(query,ensure_ascii=False)
    # print(query)
    # print(stringify_dict(query))
    try:
        result = await run_workflow(
            api_key=api_key,
            inputs=stringify_dict(query),
            response_mode="blocking",
            user="abc-123"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")

async def fill_meta_by_code(query:dict):
    api_key = "app-yIKrmWNsNFZ3k30N5Vnuf7kP"  # 替换为实际的API密钥
    # json_query = json.dumps(query,ensure_ascii=False)
    inputs=stringify_dict_2(query)
    print(type(inputs["planning"]))
    print(inputs["planning"])
    try:
        result = await run_workflow(
            api_key=api_key,
            inputs=stringify_dict_2(query),
            response_mode="blocking",
            user="abc-123"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(result["data"]["outputs"])
        return result["data"]["outputs"]
    except Exception as e:
        print(f"工作流执行失败: {e}")
        return -1

if __name__ == "__main__":
#   asyncio.run(intent_detection("富集分析"))
    #测试plan_check
    # from example import plan_desc
    # asyncio.run(plan_check(plan_desc))
    #测试recommend_images
    # from example import plan_desc_step3_ai
    # # print(plan_desc_step3_ai)
    # asyncio.run(recommend_images(plan_desc_step3_ai))
    #测试error_check
    # from example import images_error_check,data_test_1
    # asyncio.run(error_check(images_error_check))
    # asyncio.run(data_check(data_test_1))

    # from example import description_ai_auto_fill
    # d={
    #     "title": "拟时序分析",
    #     "tools": "monocle2",
    #     "step": 2,
    #     "previous_step": [
    #       "细胞聚类分析",
    #       "细胞注释"
    #     ],
    #     "description": "\nAI自动补充",
    #     "input": "",
    #     "output": ""}
    # asyncio.run(description_ai_auto_fill(d))
    #0806测试推荐数据
    plan_step={
        "title": "细胞互作分析",
        "tools": "cellchat",
        "step": 5,
        "previous_step": [
          "细胞聚类分析",
          "细胞注释"
        ],
        "name": "",
        "oid": "",
        "description": "细胞互作分析是研究细胞间通讯网络的重要方法，通过分析配体-受体对的表达模式来揭示细胞间的信号传递机制。CellChat工具利用网络分析和模式识别算法，整合单细胞RNA测序数据中的配体-受体相互作用信息，构建细胞间通讯网络。该模块能够识别不同细胞类型之间的关键信号通路，揭示细胞群体间的功能协调机制。分析结果对于理解组织微环境、细胞分化调控和疾病发生机制具有重要意义，为后续的功能研究和生物标志物发现提供重要线索。",
        "input": ".rds, .h5",
        "output": ".pdf, .png, .html, .csv",
        "plan_type": "ai",
        "raw_input_params": {
          "input": "{{Stereo_Miner_Autoannotation_v1.outh5ad}}"
        },
        "raw_output_params": {
          "ai.step5.output": "{{ai.step5.output}}"
        }
      }

    q={
        "plan_step":plan_step,
        "data_name": "sample.tissue.gef",
        "first_node": "",
        "omics":"STOmics"}
    res=asyncio.run(recommend_data(q))
