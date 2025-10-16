import json
import requests
from typing import List
# from app.core.logging import get_logger
# logger = get_logger(__name__)

def query_workflow_id(workflow_ids: List[str]) -> List[str]:
    """
    查询指定workflow_id关联节点的所有 name 并返回列表
    
    Args:
        workflow_ids: workflow_id列表
    
    Returns:
        所有匹配到的 name 列表（可能为空列表）
    """
    url = "http://10.224.28.80:10111/db/neo4j/tx/commit"
    
    headers = {
        "Authorization": "Basic bmVvNGo6ZjAxMjQ2NDk5OA==",
        "Content-Type": "application/json"
    }
    
    # 使用参数化查询，防止注入攻击
    cypher_query = """
    MATCH (n:Tools) 
    WHERE n.workflow_id IN $workflow_ids
    RETURN n.name
    """
    
    payload = {
        "statements": [
            {
                "statement": cypher_query,
                "parameters": {
                    "workflow_ids": workflow_ids  # 修复：使用正确的参数名
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()

            # 检查是否有Neo4j错误
            if result.get("errors"):
                print(f"Neo4j查询错误: {result['errors']}")
                return []

            # 解析所有 name
            results = result.get("results", [])
            if results:
                data = results[0].get("data", [])
                names = [row.get("row", [None])[0] for row in data if row.get("row") and row.get("row")[0] is not None]
                if names:
                    print(f"找到 {len(names)} 个 name: {names}")
                    return names
            
            print(f"未找到匹配的记录 - workflow_ids: {workflow_ids}")
            return []
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return []

    except Exception as e:
        print(f"请求异常: {e}")
        return []
if __name__ == "__main__":
    workflow_ids = ["67c10f2ae99e8ef1529cfc94"]
    print(query_workflow_id(workflow_ids))