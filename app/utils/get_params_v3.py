import requests
import json
import ast
import re
def parse_parameters_to_defaults(param_string,sampleid):
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
            # param_name = full_param_name.split('.')[-1]
            param_name = full_param_name

            if param_name.endswith(".SampleID"):

                default_value=sampleid
            else:
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

def get_params_v3(data_choose):
    """
    获取参数
    """
    return data_choose


if __name__ == "__main__":
    data_choose={
        "records": [
            {
                "dataType": "0",
            }
        ]
    }
    planning_result={"planning_steps": [
      {
        "title": "Stereo_Miner_Clustering",
        "tools": "",
        "step": 1,
        "name": "Stereo_Miner_Clustering",
        "description": "该工作流基于标准化表达矩阵，通过降维（如PCA、UMAP）和聚类分析（Leiden或Louvain算法）识别细胞群体及其标记基因。支持使用Stereopy或Spateo工具进行空间转录组数据的聚类分析，并生成标记基因表和可视化结果。主要输出包括聚类图、UMAP图、h5ad格式分析文件及标记基因热图等，用于揭示数据中的细胞异质性与功能特征。推荐参数设置已优化，适用于大规模细胞数据的高效分析。",
        "oid": "67921a81f72d93061c161e1e",
        "input": "[]",
        "output": "[]",
        "plan_type":"wdl",
        "raw_input": "{'StereoMiner_Clustering_v1.SampleID': 'String', 'StereoMiner_Clustering_v1.h5File': 'File', 'StereoMiner_Clustering_v1.FeatureSelection': 'String (default = \"True\")', 'StereoMiner_Clustering_v1.PcsNumber': 'Int (default = 50)', 'StereoMiner_Clustering_v1.DimensionalReduction': 'String (default = \"UMAP\")', 'StereoMiner_Clustering_v1.UsePcsNumber': 'Int (default = 30)', 'StereoMiner_Clustering_v1.NeighborhoodSize': 'Int (default = 20)', 'StereoMiner_Clustering_v1.ClusteringMethod': 'String (default = \"leiden\")', 'StereoMiner_Clustering_v1.Resolution': 'Float (default = 0.5)', 'StereoMiner_Clustering_v1.ClusteringTool': 'String (default = \"Stereopy\")'}",
        "raw_output": "{'StereoMiner_Clustering_v1.clusterPng': 'File? (optional)', 'StereoMiner_Clustering_v1.clusterPdf': 'File? (optional)', 'StereoMiner_Clustering_v1.cluster_umap': 'File? (optional)', 'StereoMiner_Clustering_v1.cluster_umap_pdf': 'File? (optional)', 'StereoMiner_Clustering_v1.cluster_anndata': 'File? (optional)', 'StereoMiner_Clustering_v1.find_marker_genes': 'File? (optional)', 'StereoMiner_Clustering_v1.marker_gene_heatmap': 'File? (optional)', 'StereoMiner_Clustering_v1.marker_gene_heatmap_pdf': 'File? (optional)'}"
      }
    ]}
    res = get_params_v3(data_choose)
    print(planning_result["planning_steps"][0]["raw_input"])
    print(parse_parameters_to_defaults(planning_result["planning_steps"][0]["raw_input"],"123"))




