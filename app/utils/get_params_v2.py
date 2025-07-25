import requests
import json
from app.utils.example import plan_steps_1,plan_steps_2,data_test_1
from app.utils.call_dify import get_filled_parametersv2,get_filled_parameters
from app.utils.run_workflow import description_ai_auto_fill


import re

import ast

def replace_values_with_placeholders(input_str):
    # 将字符串解析为字典
    input_dict = ast.literal_eval(input_str)
    
    # 替换值为占位符
    return {key: f'{{{{{key}}}}}' for key in input_dict.keys()}

def parse_parameters_to_defaults(param_string):
    """
    解析参数字符串，提取参数名和默认值
    
    Args:
        param_string (str): 参数字符串，格式如：
            "{'SAW_ST_V8_Clustering.Gef': 'File', 'SAW_ST_V8_Clustering.BinSize': 'Int? (optional, default = 200)'}"
    
    Returns:
        dict: {参数名: 默认值} 的字典，没有默认值的参数值为空字符串
    
    Example:
        >>> param_str = "{'Tool.Name': 'String (default = test)', 'Tool.Count': 'Int'}"
        >>> parse_parameters_to_defaults(param_str)
        {'Name': 'test', 'Count': ''}
    """
    try:
        # 将字符串转换为字典
        param_dict = ast.literal_eval(param_string)
        
        # 存储结果的字典
        result = {}
        
        for full_param_name, param_type in param_dict.items():
            # 提取参数名（去掉前缀）
            param_name = full_param_name.split('.')[-1]
            
            # 查找默认值
            default_value = ""
            
            # 使用正则表达式匹配默认值
            # 匹配模式：default = 值
            default_match = re.search(r'default\s*=\s*([^)]+)', param_type, re.IGNORECASE)
            
            if default_match:
                default_str = default_match.group(1).strip()
                
                # 处理不同类型的默认值
                if default_str.lower() == 'true':
                    default_value = True
                elif default_str.lower() == 'false':
                    default_value = False
                elif default_str.isdigit():
                    default_value = int(default_str)
                elif re.match(r'^\d+\.\d+$', default_str):
                    default_value = float(default_str)
                else:
                    # 保持原始字符串，去掉可能的引号
                    default_value = default_str.strip('\'"')
            
            result[param_name] = default_value
        
        return result
    
    except Exception as e:
        print(f"解析错误: {e}")
        return {}

def neo4j_query(statements):
    """
    执行 Neo4j Cypher 查询
    
    Args:
        statements: 查询语句，可以是字符串或语句列表
        
    Returns:
        dict: Neo4j 响应结果
    """
    url = "http://10.224.28.80:10104/db/neo4j/tx/commit"
    headers = {
        "Authorization": "Basic bmVvNGo6ZjAxMjQ2NDk5OA==",
        "Content-Type": "application/json"
    }
    
    # 处理输入参数
    if isinstance(statements, str):
        # 如果是字符串，转换为标准格式
        data = {"statements": [{"statement": statements}]}
    elif isinstance(statements, list):
        # 如果是列表，检查格式
        if statements and isinstance(statements[0], str):
            # 字符串列表，转换格式
            data = {"statements": [{"statement": stmt} for stmt in statements]}
        else:
            # 已经是标准格式
            data = {"statements": statements}
    else:
        # 直接使用（假设已经是正确格式）
        data = {"statements": statements}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()



def output_node_info(dify_result):
    # print("dify_result:",dify_result)
    n=1
    final_result_list=[] 

    for i in dify_result:
        # print("i:",i)
        # print("i['model_id']:",i["model_id"])
        i_dict={}
        is_app=True
        i_dict["title"]=i["title"]
        i_dict["tools"]=i["tools"]
        i_dict["step"]=n
        try:
            # i["model_id"]=int(i["model_id"])
            # get_node_dependon="MATCH (n {model_id: %d}) RETURN n" % i["model_id"]
            # # print("get_node_dependon:",get_node_dependon)
            # res_dependon=neo4j_query(get_node_dependon)
            # print("res_dependon:",res_dependon)
            i_dict["previous_step"]=i["previous_step"]
            # print("i_dict['previous_step']:",i_dict["previous_step"])
            if i["tools"] != "":
                is_app=False
        except Exception as e:
            print("e:",e)
            i_dict["previous_step"]=""
            is_app=False
    
        if is_app:
            # get_node_by_contain_relationship="MATCH (n {model_id: %d})-[:contain]->(other) RETURN other LIMIT 1" % i["model_id"]
            get_node_by_contain_relationship="MATCH (n {name: '%s'}) RETURN n" % i["name"]
            # print("get_node_by_contain_relationship:",get_node_by_contain_relationship)
            app_nodes=neo4j_query(get_node_by_contain_relationship)
            # print("app_nodes:",app_nodes)
            try:
                app_nodes=app_nodes["results"][0]["data"][0]["row"]
            except Exception as e:
                print("e:",e)
                app_nodes=app_nodes["results"][0]["data"]
            # print("app_nodes:",app_nodes)
            if len(app_nodes) > 0:
                i_dict["name"]=app_nodes[0]["workflow_name"]
                i_dict["oid"]=app_nodes[0]["workflow_id"]
                i_dict["description"]=app_nodes[0]["summary_short"]
                i_dict["input"]=app_nodes[0]["input_files"]
                i_dict["output"]=app_nodes[0]["output_files"]
                i_dict["plan_type"]="wdl"
                i_dict["raw_input_params"]=app_nodes[0]["inputs"]
                i_dict["raw_output_params"]=app_nodes[0]["raw_output"]
                final_result_list.append(i_dict)
            
            else:
                i_dict["name"]=""
                i_dict["oid"]=""
                i_dict["description"]=""
                i_dict["input"]=""
                i_dict["output"]=""
                i_dict["plan_type"]="ai"
                i_dict["raw_input_params"]='{"input":""}'
                i_dict["raw_output_params"]='{{"ai.step{num}.output":""}}'.format(num=n)
                final_result_list.append(i_dict)
            n+=1
        else:
            i_dict["name"]=""
            i_dict["oid"]=""
            i_dict["description"]=""
            i_dict["input"]=""
            i_dict["output"]=""
            i_dict["plan_type"]="ai"
            i_dict["raw_input_params"]='{"input":""}'
            i_dict["raw_output_params"]='{{"ai.step{num}.output":""}}'.format(num=n)
            final_result_list.append(i_dict)
            n+=1
    return final_result_list


async def chuli_raw_planing(raw_params,file_path):
    user = "abc-123"
    conversation_id = "1234567890"
    response_mode = "blocking"
    process_steps=[]
    step_depend_on=[]
    final_result_list=[]

    index_last_step=0
    for i in raw_params:

        if i["plan_type"] == "ai":
            # print("i:",i)
            ai_auto_fill_result=await description_ai_auto_fill(i)
            i["description"]=ai_auto_fill_result["structured_output"]["description"]
            i["input"]=ai_auto_fill_result["structured_output"]["input"]
            i["output"]=ai_auto_fill_result["structured_output"]["output"]
            if i["tools"] == "":
                i["tools"]=ai_auto_fill_result["structured_output"]["tools"]
        if i["step"] == 1:
            if i["plan_type"] == "wdl":
                query_template=parse_parameters_to_defaults(i["raw_input_params"])
                data_choose=json.dumps(file_path)
                i["raw_input_params"]=await get_filled_parameters(data_choose=data_choose,query_template=query_template,user=user,conversation_id=conversation_id,response_mode=response_mode)
                i["raw_output_params"]=replace_values_with_placeholders(i["raw_output_params"])
                # print("ai自动填写参数input:",i["raw_input_params"])
                # print("ai自动填写参数output:",i["raw_output_params"])
            else:
                print("固定补充")
                i["raw_output_params"]="{{{{ai.step1.output}}}}"
                i["raw_input_params"]=file_path


            if i["previous_step"] not in step_depend_on:
                step_depend_on.append(i["previous_step"])
                process_steps.append(i)
            else:
                print("触发了并行")
            final_result_list.append(i)
        else:
            # print("i:",i)
            if i["previous_step"] not in step_depend_on:
                step_depend_on.append(i["previous_step"])
                process_steps.append(i)
                last_step=process_steps[index_last_step]
                index_last_step=index_last_step+1
            else:
                print("触发了并行")
                index_last_step=index_last_step-1
                last_step=process_steps[index_last_step]
            print("index_last_step:",index_last_step)
            
            last_step_output=last_step["raw_output_params"]
            # print("last_step_output:",last_step_output)
            # print("i['raw_input_params']:",i["raw_input_params"])
            input_this_step=parse_parameters_to_defaults(i["raw_input_params"])
            if last_step["plan_type"] == "wdl":
                last_step_output=json.dumps(last_step_output)
                # print("last_step_output:",last_step_output)
                # print("999999999")
                # print(input_this_step)
                i["raw_input_params"]=await get_filled_parametersv2(data_choose=last_step_output,query_template=input_this_step,user=user,conversation_id=conversation_id,response_mode=response_mode)
                i["raw_output_params"]=replace_values_with_placeholders(i["raw_output_params"])
                print("ai自动填写参数:",i["raw_input_params"])
            else:
                print("AI补充输入，固定补充输出")
                i["raw_input_params"]=last_step_output
                i["raw_output_params"]="{{{{ai.step{num}.output}}}}".format(num=i["step"])

            final_result_list.append(i)
    # print("step_depend_on:",step_depend_on)
    return final_result_list

import asyncio

async def main_request(arg1:dict,file_path:dict) -> dict:
    # print("arg1:",arg1)
    try:
        final_result_list=output_node_info(arg1["planning_steps"])
    except Exception as e:
        print(e)
    print("111")
    final_result_list=await chuli_raw_planing(final_result_list,file_path)


    return {"result":final_result_list}

if __name__ == "__main__":
    from example import test_auto_fill_params
    res = asyncio.run(main_request(plan_steps_1,data_test_1))
    print(res)
    rrr=asyncio.run(main_request(test_auto_fill_params,data_test_1))
    print(rrr)