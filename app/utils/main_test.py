from run_workflow import recommend_data,fill_params_images,fill_meta_by_code
import asyncio

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
plan_step_v2=  {
    "title": "细胞互作分析",
    "tools": "",
    "step": 5,

    "previous_step": [],

    "name": "",
    "oid": "",
    "description": "",
    "input": "",
    "output": "",
    "plan_type": "ai",
    "raw_input_params": {
      "input": ""
    },
    "raw_output_params": {
      "ai.step5.output": ""
    }
  }
code_content='''import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 设置scanpy参数
sc.settings.verbosity = 3  # 详细输出
sc.settings.set_figure_params(dpi=80, facecolor='white')

def perform_clustering_analysis(input_file, output_dir):
  """
  基于scanpy进行单细胞聚类分析
  
  Parameters:
  -----------
  input_file : str
      输入的h5ad文件路径
  output_dir : str
      输出目录路径
  """
  
  # 创建输出目录
  output_path = Path(output_dir)
  output_path.mkdir(parents=True, exist_ok=True)
  
  # 1. 读取数据
  print("正在读取数据...")
  adata = sc.read_h5ad(input_file)
  
  # 2. 数据预处理（如果还未完成）
  print("进行数据预处理...")
  
  # 计算高变基因
  sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
  sc.pl.highly_variable_genes(adata)
  plt.savefig(output_path / "highly_variable_genes.png", dpi=300, bbox_inches='tight')
  plt.close()
  
  # 保留高变基因
  adata.raw = adata
  adata = adata[:, adata.var.highly_variable]
  
  # 标准化和log转换
  sc.pp.scale(adata, max_value=10)
  
  # 3. 主成分分析
  print("进行主成分分析...")
  sc.tl.pca(adata, svd_solver='arpack')
  sc.pl.pca_variance_ratio(adata, log=True, n_pcs=50)
  plt.savefig(output_path / "pca_variance.png", dpi=300, bbox_inches='tight')
  plt.close()
  
  # 4. 计算邻域图
  print("计算邻域图...")
  sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
  
  # 5. UMAP降维
  print("进行UMAP降维...")
  sc.tl.umap(adata)
  
  # 6. Leiden聚类
  print("进行Leiden聚类...")
  # 尝试不同的分辨率
  resolutions = [0.1, 0.3, 0.5, 0.7, 1.0]
  
  for res in resolutions:
      sc.tl.leiden(adata, resolution=res, key_added=f'leiden_res_{res}')
  
  # 7. 可视化聚类结果
  print("生成聚类可视化图...")
  
  # UMAP图显示不同分辨率的聚类结果
  fig, axes = plt.subplots(2, 3, figsize=(18, 12))
  axes = axes.flatten()
  
  # 原始UMAP
  sc.pl.umap(adata, ax=axes[0], show=False, frameon=False, title='Original UMAP')
  
  # 不同分辨率的聚类结果
  for i, res in enumerate(resolutions):
      sc.pl.umap(adata, color=f'leiden_res_{res}', ax=axes[i+1], 
                show=False, frameon=False, title=f'Leiden (res={res})')
  
  plt.tight_layout()
  plt.savefig(output_path / "clustering_comparison.png", dpi=300, bbox_inches='tight')
  plt.close()
  
  # 8. 选择最佳分辨率（这里选择0.5作为示例）
  best_resolution = 0.5
  adata.obs['leiden'] = adata.obs[f'leiden_res_{best_resolution}']
  
  # 9. 聚类质量评估
  print("评估聚类质量...")
  
  # 计算silhouette score
  from sklearn.metrics import silhouette_score
  
  # 使用PCA坐标计算silhouette score
  silhouette_avg = silhouette_score(adata.obsm['X_pca'][:, :10], 
                                   adata.obs['leiden'].astype(int))
  
  print(f"平均Silhouette Score: {silhouette_avg:.3f}")
  
  # 10. 聚类统计信息
  cluster_stats = adata.obs['leiden'].value_counts().sort_index()
  
  # 保存聚类统计
  cluster_stats.to_csv(output_path / "cluster_statistics.csv", header=['Cell_Count'])
  
  # 11. 生成最终的UMAP图
  plt.figure(figsize=(12, 8))
  sc.pl.umap(adata, color='leiden', legend_loc='on data', 
            title=f'Leiden Clustering (resolution={best_resolution})',
            frameon=False, save=False)
  plt.savefig(output_path / "final_clustering_umap.png", dpi=300, bbox_inches='tight')
  plt.close()
  
  # 12. 聚类热图
  plt.figure(figsize=(10, 8))
  sc.pl.umap(adata, color='leiden', palette='tab20')
  plt.savefig(output_path / "clustering_heatmap.png", dpi=300, bbox_inches='tight')
  plt.close()
  
  # 13. 保存结果
  print("保存分析结果...")
  
  # 保存包含聚类信息的adata对象
  adata.write(output_path / "clustered_data.h5ad")
  
  # 保存聚类结果表格
  cluster_df = pd.DataFrame({
      'cell_id': adata.obs.index,
      'cluster': adata.obs['leiden'],
      'umap_1': adata.obsm['X_umap'][:, 0],
      'umap_2': adata.obsm['X_umap'][:, 1]
  })
  cluster_df.to_csv(output_path / "clustering_results.csv", index=False)
  
  # 14. 生成分析报告
  report = f"""
  聚类分析报告
  ============
  
  输入文件: {input_file}
  细胞总数: {adata.n_obs}
  基因总数: {adata.n_vars}
  聚类数量: {len(cluster_stats)}
  最佳分辨率: {best_resolution}
  平均Silhouette Score: {silhouette_avg:.3f}
  
  各聚类细胞数量:
  {cluster_stats.to_string()}
  
  输出文件:
  - clustered_data.h5ad: 包含聚类信息的数据对象
  - clustering_results.csv: 聚类结果表格
  - final_clustering_umap.png: 最终聚类UMAP图
  - clustering_comparison.png: 不同分辨率比较图
  - cluster_statistics.csv: 聚类统计信息
  """
  
  with open(output_path / "clustering_report.txt", 'w', encoding='utf-8') as f:
      f.write(report)
  
  print("聚类分析完成！")
  print(f"结果保存在: {output_path}")
  
  return adata

# 使用示例
if __name__ == "__main__":
  # 输入输出路径
  input_file = "preprocessed_data.h5ad"  # 预处理后的数据
  output_dir = "clustering_results"
  
  # 执行聚类分析
  clustered_adata = perform_clustering_analysis(input_file, output_dir)
  
  # 可选：进一步分析
  print("\n聚类完成，可以进行后续分析：")
  print("- 差异基因分析")
  print("- 细胞类型注释") 
  print("- 功能富集分析")
'''

if __name__ == "__main__":

    q={
        "plan_step":plan_step,
        "data_name": "sample.tissue.gef",
        "first_node": "",
        "omics":"STOmics"}
    # res=asyncio.run(recommend_data(q))
    # res=asyncio.run(fill_params_images({"plan":plan_step}))
    q={
        "coding":code_content,
        "planning":plan_step_v2}
    res=asyncio.run(fill_meta_by_code(q))