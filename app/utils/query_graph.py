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


def get_output_format(tool_names):
    ret = defaultdict(list)
    inquired_data_state = query_cypher("""MATCH (n:Tools)-[r:output_format]->(m:DataState) WHERE n.workflow_id IN $tool RETURN n.workflow_id, m.name""", parameters={'tool': tool_names}, return_type='list')
    for x in inquired_data_state:
        ret[x.data()['n.workflow_id']].append(x.data()['m.name'])
    return {x: list(set(y)) for x, y in ret.items() }

    
def get_tools_from_datastate(data_state):
    # cypher = """MATCH (m:Tools)-[r:output_format]->(n:DataState) 
    # OPTIONAL MATCH (x:DataState)-[r:input_requirement]->(m:Tools)-[r:output_format]->(n:DataState)
    # WHERE n.name = $data_state 
    # RETURN x.name, m.name"""
    cypher = """MATCH (m:Tools)-[r:output_format]->(n:DataState) 
    WHERE n.name = $data_state 
    RETURN m.name"""
    inquired_data_state = query_cypher(cypher, parameters={'data_state': data_state}, return_type='list')
    result = []
    for x in inquired_data_state:
        result.append( x.data()['m.name'])
    return result


def check_matrix_status(status):
    if 'scale' in status:
        ret = [x for x in status if (x != 'raw') & (x != 'lognormalize')]
    elif 'lognormalize' in status:
        ret = [x for x in status if x != 'raw']
    else:
        return status
    return ret


def check_pipeline_validation(pipeline, tools2input, tools2output, preloading):
    current_status = preloading
    for x in pipeline:
        if len(set(tools2input[x]) - set(current_status)) == 0:
            
            current_status = check_matrix_status(set(current_status) | set(tools2output[x]))
            # print(current_status)
        else:
            return False
    return True


def check_pipeline_validation_set(pipeline, tools2input, tools2output, preloading):
    current_status = preloading
    for x in pipeline:
        if len(set(tools2input[x]) - set(current_status)) == 0:
            
            current_status = check_matrix_status(set(current_status) | set(tools2output[x]))
            # print(current_status)
        else:
            return set(tools2input[x]) - set(current_status)
    return {}
    

def insert_pipeline(pipe, no_include_tool, tools2input, tools2output, preloading):
    ret_pipe = [pipe]
    
    for ins_tool in no_include_tool:
        tmp_pipe = []
        for cur_pipe in ret_pipe:
            for i in range(len(cur_pipe)+1):
                new_pipe = cur_pipe.copy()
                new_pipe.insert(i, ins_tool)
                #print(new_pipe)
                if check_pipeline_validation(new_pipe, tools2input, tools2output, preloading):
                    tmp_pipe.append(new_pipe)
        ret_pipe = tmp_pipe
    return ret_pipe


def calculate_score(pipeline, tool2score):
    score = np.mean([tool2score[x] for x in pipeline])
    return score/ np.sqrt(len(pipeline))

# helper function

# def plot_tool_names(id_list, id2name = id2name):
#     return [id2name[x] for x in id_list]


def get_possible_pipeline(tool_names, preloading, project):
    url = "bolt://10.224.28.80:10112"
    auth = ("neo4j", "f012464998")  
    
    config(url, auth=auth)
    # get available tool ids 
    all_tool_list = query_cypher(f"MATCH (n:Tools)-[r:belongs_to]->(p:Project) WHERE p.id in ['{project}', 'Public'] return n.workflow_id, n.name, n.citation")
    all_tool_id_list = all_tool_list['n.workflow_id'].to_list()
    
    copied_public_tools = query_cypher(f"""MATCH (n:Tools)-[r:copy_from]->(m:Tools) 
    WHERE n.workflow_id in $all_tool_id_list 
    AND m.workflow_id in $all_tool_id_list
    return m.workflow_id""", parameters={'all_tool_id_list':all_tool_id_list})['m.workflow_id'].tolist()
    
    all_tool_list = all_tool_list.loc[~all_tool_list['n.workflow_id'].isin([copied_public_tools])]
    all_tool_id_list = all_tool_list['n.workflow_id'].to_list()
    
    # get tool input and output
    tools2input = get_input_requirement(all_tool_id_list)
    tools2output = get_output_format(all_tool_id_list)
    
    for x in all_tool_id_list:
        if x not in tools2input:
            tools2input[x] = []
        if x not in tools2output:
            tools2output[x] = []
    
    # define tool list to be query
    query_tool_list = []
    for x in all_tool_id_list:
        if len(set(tools2output[x]) - set(preloading)) > 0 :
            query_tool_list.append(x)
    
    for x in all_tool_list.loc[all_tool_list['n.name'].isin(tool_names), 'n.workflow_id'].tolist():
        if x not in query_tool_list:
            query_tool_list.append(x)
    
    id2name = dict(zip(all_tool_list['n.workflow_id'], all_tool_list['n.name']))
    
    # core query 
    cypher = """MATCH p=(m:Tools)-[r*0..7]->(n:Tools) 
    WHERE n.name IN $tool
    AND ALL(node IN nodes(p) WHERE 
        node:Tools AND node.workflow_id IN $all_tool_id_list 
        OR NOT node:Tools)
    RETURN [node IN nodes(p) WHERE node:Tools | node.workflow_id] AS workflow_id"""
    # tik = time.time()
    df = query_cypher(cypher, parameters={'tool':tool_names, 'all_tool_id_list':query_tool_list})
    df = df.fillna('')
    
    all_possible_pipeline = {'pipeline':[], 'pure_requirement':[]}
    
    for _, row in df.iterrows():
        pipeline = [x for x in list(row) if len(x)>0]
        pure_requirement = check_pipeline_validation_set(pipeline, tools2input, tools2output, preloading)
        all_possible_pipeline['pipeline'].append(pipeline) 
        all_possible_pipeline['pure_requirement'].append(pure_requirement)
    # tok = time.time()
    # print(tok - tik)
    all_possible_pipeline = pd.DataFrame(all_possible_pipeline)
    
    all_possible_pipeline['end'] = [x[-1] for x in all_possible_pipeline['pipeline']]
    all_possible_pipeline["pure_requirement_length"] = [len(x) for x in all_possible_pipeline['pure_requirement']]
    
    target_tool_ids = []
    for x in tool_names:
        target_tool_ids.append(all_tool_list.loc[all_tool_list['n.name'] == x].sort_values('n.citation', ascending=False)['n.workflow_id'].tolist()[0])
    
    all_tool_list.loc[all_tool_list['n.workflow_id'].isin(target_tool_ids), 'n.citation'] = 10000
    
    tool2score = dict(zip(all_tool_list['n.workflow_id'], all_tool_list['n.citation']))
    
    result = {"success":True, 
                  "possible_pipeline":[], 
                  "require_data_states":[]
                 }
    
    valid_pipeline = []
    for x, y in all_possible_pipeline.groupby('end'):
        validate_y = y.loc[y['pure_requirement_length']==0]
        if validate_y.shape[0]==0:
            result["success"] = False
            result['require_data_states'] = {x : list(set(tools2input[x]) - set(preloading))}
            return result
            break
        else:
            valid_pipeline.append(validate_y)
    valid_pipeline = pd.concat(valid_pipeline)
    valid_pipeline['no_include_tool'] = [list(set(target_tool_ids) - set(p)) for p in valid_pipeline['pipeline']]
    valid_pipeline['no_include_tool_length'] = [len(x) for x in valid_pipeline['no_include_tool']]
    min_undo_tools = valid_pipeline['no_include_tool_length'].min()
            
    if min_undo_tools == 0:
        result['possible_pipeline'] = list(valid_pipeline.loc[valid_pipeline['no_include_tool_length'] == min_undo_tools]['pipeline'])
    else:
        new_inserted_pipeline = []
        # return valid_pipeline
        valid_pipeline = valid_pipeline.loc[valid_pipeline['no_include_tool_length'] == min_undo_tools]
        for pipe, no_include_tool in zip(valid_pipeline['pipeline'], valid_pipeline['no_include_tool']):
            for x in insert_pipeline(pipe, no_include_tool, tools2input, tools2output, preloading):
                new_inserted_pipeline.append(x)
        result['possible_pipeline'] = new_inserted_pipeline
    
    # scoring system
    if result['success']:
        pipelines = result['possible_pipeline']
        scores = [calculate_score(p, tool2score) for p in pipelines]
        select_pipelines = list(np.argsort(scores)[::-1][:5])
        select_pipelines = [pipelines[x] for  x in select_pipelines]
        result['possible_pipeline'] = select_pipelines

    return result

if __name__ == "__main__":
    url = "bolt://10.224.28.80:10112"
    auth = ("neo4j", "f012464998")  
    
    config(url, auth=auth)
    
    tool_names = ['GraphST_Tutorial', 'Stereo_Miner_Clustering']
    preloading = [ "raw", "qc", 'spatial']
    project = 'P20250228091931671'
    
    result = get_possible_pipeline(tool_names, preloading, project)
    print(result)

