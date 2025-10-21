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
    return {x: list(set(y)) for x, y in ret.items() }



# helper function
def replace_tools(old_tool_id):
    url = "bolt://10.224.28.80:10112"
    auth = ("neo4j", "f012464998")  
    config(url, auth=auth)
    project_id = query_cypher(f"MATCH (n:Tools {{workflow_id: '{old_tool_id}'}})-[r:belongs_to]->(m:Project) return m.id", return_type='list')[0].data()['m.id']
    task = query_cypher(f"MATCH (n:Tools {{workflow_id: '{old_tool_id}'}})-[r:belongs_to]->(m:Task) return m.name", return_type='list')[0].data()['m.name']
    
    all_tool_list = query_cypher(f"MATCH (n:Tools)-[r:belongs_to]->(p:Project) WHERE p.id in ['{project_id}', 'Public'] AND (n)-[:belongs_to]->(:Task {{name: '{task}'}}) return n.workflow_id, n.name, n.citation, p.id")
    all_tool_id_list = all_tool_list['n.workflow_id'].to_list()
    
    copied_public_tools = query_cypher(f"""MATCH (n:Tools)-[r:copy_from]->(m:Tools) 
    WHERE n.workflow_id in $all_tool_id_list 
    AND m.workflow_id in $all_tool_id_list
    return m.workflow_id""", parameters={'all_tool_id_list':all_tool_id_list})['m.workflow_id'].tolist()
    
    all_tool_list = all_tool_list.loc[~all_tool_list['n.workflow_id'].isin(copied_public_tools)]
    all_tool_id_list = all_tool_list['n.workflow_id'].to_list()

    tools2input = get_input_requirement(all_tool_id_list)
    for x in all_tool_id_list:
        if x not in tools2input:
            tools2input[x] = []
    all_tool_list['input_requirement'] = [tools2input[x] for x in all_tool_list['n.workflow_id']]
    all_tool_list = all_tool_list.loc[all_tool_list['n.workflow_id'] != old_tool_id]
    old_input = tools2input[old_tool_id]
    all_tool_list['input_similiarity'] = [1 - len(set(x) - set(old_input))/(2*len(set(x))) if len(set(x)) != 0 else 1 for x in all_tool_list['input_requirement']]
    all_tool_list['score'] = all_tool_list['n.citation'] * all_tool_list['input_similiarity'] 
    result = all_tool_list.sort_values('score', ascending=False).head(10)
    return {x: list(y['n.workflow_id']) for x, y in result.groupby('p.id')}

if __name__ == "__main__":


    old_tool_id = '68b67fa5c1808feae021d8e6'
    res = replace_tools(old_tool_id)
    print(res)