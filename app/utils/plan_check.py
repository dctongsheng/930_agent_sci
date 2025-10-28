# 原生python
from collections.abc import Sequence
from collections import defaultdict
# 第三方包
import pandas as pd
import numpy as np
import networkx as nx
from neo4j import GraphDatabase


_driver_instance = None

def config(url, auth=None, encrypted=False):
    """
    Configures the database connection and initializes the global driver instance.

    Args:
        url (str): The database connection URL (e.g., "bolt://localhost:7687").
        auth (tuple, optional): A tuple containing authentication credentials (username, password). Defaults to None.
        encrypted (bool, optional): Whether to enable encrypted communication. Defaults to False.

    Returns:
        None
    """
    global _driver_instance
    _driver_instance = GraphDatabase.driver(url, auth=auth, encrypted=encrypted)
    print(f"Graph database has been configured and initialized successfully.")

    # if _driver_instance is None:
    #     _driver_instance = GraphDatabase.driver(url, auth=auth, encrypted=encrypted)
    # else:
    #     raise RuntimeError("Database has already been configured!")

def get_driver():
    """
    Retrieves the global driver instance.

    Returns:
        GraphDatabase.driver or None: The configured driver instance if available, otherwise None.
    """
    if _driver_instance is None:
        raise RuntimeError("Database has not been configured. Call BRICK.config(url) first.")
    return _driver_instance

def _flatten_dict(nested_dict, parent_key='', sep='.'):
    """ 
    Recursively flattens a nested dictionary (including lists) into a single-layer dictionary, 
    where keys represent the nested paths.

    Args:
        nested_dict (dict): The nested dictionary, which may contain lists or other nested dictionaries.
        parent_key (str, optional): The parent key for the current recursion level, defaults to an empty string.
        sep (str, optional): The separator used to connect the nested keys, defaults to '.'.

    Returns:
        dict: A flattened dictionary with keys as the path of the nested structure and values as the corresponding elements.
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(_flatten_dict(value, new_key, sep).items())
        elif isinstance(value, list):
            for i, sub_value in enumerate(value):
                if isinstance(sub_value, (dict, list)):
                    sub_items = _flatten_dict(sub_value, f"{new_key}{sep}{i}", sep)
                    items.extend(sub_items.items())
                else:
                    items.append((f"{new_key}{sep}{i}", sub_value))
        else:
            items.append((new_key, value))
    return dict(items)
    
def query_cypher(cypher, parameters=None, return_type='dataframe'):
    """
    Executes a Cypher query and returns the query result. The output format is determined by the `return_type` parameter, 
    which supports returning a Pandas DataFrame, a NetworkX MultiDiGraph, or a list.

    Args:
        cypher (str): The Cypher query string to be executed.
        parameters (dict or None, optional): Query parameters (default is None). If needed, parameters can be passed to the query.
        return_type (str): Specifies the format of the returned object. Available options:
            - 'dataframe': Returns the result as a Pandas DataFrame.
            - 'graph': Returns the result as a NetworkX MultiDiGraph.
            - 'list': Returns the result as a list of records.

    Returns:
        - If `return_type` is 'dataframe', returns a Pandas DataFrame containing the query results.
        - If `return_type` is 'graph', returns a NetworkX MultiDiGraph containing nodes and edges.
        - If `return_type` is 'list', returns a list of records.
    """
    driver = get_driver()

    if return_type not in ['dataframe', 'graph', 'list']:
        raise ValueError("return_type must be chosen from ['dataframe', 'graph']")

    if return_type == 'dataframe':
        with driver.session() as session:
            #print(driver)
            result = session.run(cypher, parameters)
            original_result = [record for record in result]
        
        result = [record.data() for record in original_result]
        result = [_flatten_dict(x) for x in result]
        result = pd.DataFrame(result)

        if 'path.1' in result:
            edges_properties = []
            for record in original_result:
                tmp_dict = {}
                for i, j in enumerate([i._properties for i in record['path'].relationships]):
                    for x, y in j.items():
                        tmp_dict[f"path.{2*i+1}.{x}"] = y
                edges_properties.append(tmp_dict)
            edges_properties = pd.DataFrame(edges_properties)
    
            result = pd.concat([result, edges_properties], axis = 1)
            result = result[sorted(result.columns)]

    elif return_type =='graph':
        with driver.session() as session:
            #print(driver)
            result = session.run(cypher, parameters)
            result = result.graph()
        assert len(result.nodes) > 0, "The cypher should return nodes, edges or paths.\
         i.e. 'MATCH path=(n)-[r]-(m) RETURN path LIMIT 10'"
        result = _neo4j2networkx(result)
    
    elif return_type == 'list':
        with driver.session() as session:
            #print(driver)
            result = session.run(cypher, parameters)
            result = [record for record in result]

    return result


def get_input_requirement(tool_names):
    ret = defaultdict(list)
    inquired_data_state = query_cypher("""MATCH (m:DataState)-[r:input_requirement]->(n:Tools) WHERE n.workflow_id IN $tool RETURN n.workflow_id, m.name""", parameters={'tool': tool_names}, return_type='list')
    for x in inquired_data_state:
        ret[x.data()['n.workflow_id']].append(x.data()['m.name'])
    ret = {x: list(set(y)) for x, y in ret.items() }
    for x in tool_names:
        if x not in ret:
            ret[x] = []
    return ret


def get_output_format(tool_names):
    ret = defaultdict(list)
    inquired_data_state = query_cypher("""MATCH (n:Tools)-[r:output_format]->(m:DataState) WHERE n.workflow_id IN $tool RETURN n.workflow_id, m.name""", parameters={'tool': tool_names}, return_type='list')
    for x in inquired_data_state:
        ret[x.data()['n.workflow_id']].append(x.data()['m.name'])
    ret = {x: list(set(y)) for x, y in ret.items() }
    for x in tool_names:
        if x not in ret:
            ret[x] = []
    return ret

def get_workflow_name(pipeline_id):
    ret = {}
    inquired_data_state = query_cypher("""MATCH (n:Tools) WHERE n.workflow_id IN $tool RETURN n.workflow_id, n.name""", parameters={'tool': pipeline_id}, return_type='list')
    for x in inquired_data_state:
        ret[x.data()['n.workflow_id']] = x.data()['n.name']
    return ret

def check_matrix_status(status):
    if 'scale' in status:
        ret = [x for x in status if (x != 'raw') & (x != 'lognormalize')]
    elif 'lognormalize' in status:
        ret = [x for x in status if x != 'raw']
    else:
        return status
    return ret

def plan_check(pipeline, preloading):
    url = "bolt://10.224.28.80:10112"
    auth = ("neo4j", "f012464998")  
    
    config(url, auth=auth)
    pipeline_id = [x['oid'] for x in pipeline['planning_steps']]
    tools2input = get_input_requirement(pipeline_id)
    tools2output = get_output_format(pipeline_id)
    current_status = preloading
    id2name = get_workflow_name(pipeline_id)
    for x in pipeline_id:
        if len(set(tools2input[x]) - set(current_status)) == 0:
            
            current_status = check_matrix_status(set(current_status) | set(tools2output[x]))
            # print(current_status)
        else:
            return {
                     "code": 200,
                     "message": "Success",
                     "check_result": {
                       "llm_output": {
                         "plan_checkout": "0",
                         "checkout_desc": f"{id2name[x]} 流程需要数据状态{'、'.join(list(set(tools2input[x]) - set(current_status)))},而原始数据与流程均不包含这种状态"
                       }
                     }
                   }
    return {
             "code": 200,
             "message": "Success",
             "check_result": {
               "llm_output": {
                 "plan_checkout": "1",
                 "checkout_desc": ""
               }
             }
           }


if __name__ == "__main__":
    url = "bolt://10.224.28.80:10112"
    auth = ("neo4j", "f012464998")  
    
    config(url, auth=auth)
    
    pipeline = {"planning_steps": [
          {
            "title": "Stereo_Miner_Clustering",
            "tools": "",
            "step": 1,
            "name": "Stereo_Miner_Clustering",
            "description": "该工作流基于标准化表达矩阵，通过降维（如PCA、UMAP）和聚类分析（Leiden或Louvain算法）识别细胞群体及其标记基因。支持使用Stereopy或Spateo工具进行空间转录组数据的聚类分析，并生成标记基因表和可视化结果。主要输出包括聚类图、UMAP图、h5ad格式分析文件及标记基因热图等，用于揭示数据中的细胞异质性与功能特征。推荐参数设置已优化，适用于大规模细胞数据的高效分析。",
            "oid": "68f74033875b1c5e5b311c7d",
            "input": "[]",
            "output": "[]",
            "raw_input_params": "{'StereoMiner_Clustering_v1.SampleID': 'String', 'StereoMiner_Clustering_v1.h5File': 'File', 'StereoMiner_Clustering_v1.FeatureSelection': 'String (default = \"True\")', 'StereoMiner_Clustering_v1.PcsNumber': 'Int (default = 50)', 'StereoMiner_Clustering_v1.DimensionalReduction': 'String (default = \"UMAP\")', 'StereoMiner_Clustering_v1.UsePcsNumber': 'Int (default = 30)', 'StereoMiner_Clustering_v1.NeighborhoodSize': 'Int (default = 20)', 'StereoMiner_Clustering_v1.ClusteringMethod': 'String (default = \"leiden\")', 'StereoMiner_Clustering_v1.Resolution': 'Float (default = 0.5)', 'StereoMiner_Clustering_v1.ClusteringTool': 'String (default = \"Stereopy\")'}",
            "raw_output_params": "{'StereoMiner_Clustering_v1.clusterPng': 'File? (optional)', 'StereoMiner_Clustering_v1.clusterPdf': 'File? (optional)', 'StereoMiner_Clustering_v1.cluster_umap': 'File? (optional)', 'StereoMiner_Clustering_v1.cluster_umap_pdf': 'File? (optional)', 'StereoMiner_Clustering_v1.cluster_anndata': 'File? (optional)', 'StereoMiner_Clustering_v1.find_marker_genes': 'File? (optional)', 'StereoMiner_Clustering_v1.marker_gene_heatmap': 'File? (optional)', 'StereoMiner_Clustering_v1.marker_gene_heatmap_pdf': 'File? (optional)'}",
            "plan_type": "wdl",
            "previous_step": ""
          }
        ]}
    
    preloading = ['spatial']
    
    plan_check(pipeline, preloading)
    print(plan_check(pipeline, preloading))
