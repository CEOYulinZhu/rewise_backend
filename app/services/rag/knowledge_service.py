"""
知识服务

管理和检索物品处置相关的知识库
"""

from typing import Dict, Any, List
import chromadb
from app.core.config import settings
from app.core.logger import app_logger


class KnowledgeService:
    """知识服务类"""
    
    def __init__(self):
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name
        )
    
    async def search_knowledge(
        self,
        category: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """搜索相关知识"""
        
        app_logger.info(f"搜索知识: 类别={category}, 关键词={keywords}")
        
        try:
            # 构造查询文本
            query_text = f"{category} {' '.join(keywords)}"
            
            # 从向量数据库搜索
            results = self.collection.query(
                query_texts=[query_text],
                n_results=5
            )
            
            # 整理返回结果
            knowledge = {
                "disposal_methods": [],
                "creative_ideas": [],
                "market_insights": [],
                "recycling_info": []
            }
            
            if results['documents']:
                for doc in results['documents'][0]:
                    # 这里可以根据文档内容分类
                    knowledge["disposal_methods"].append(doc)
            
            app_logger.info("知识搜索完成")
            return knowledge
            
        except Exception as e:
            app_logger.error(f"知识搜索失败: {e}")
            return {
                "disposal_methods": [],
                "creative_ideas": [],
                "market_insights": [],
                "recycling_info": []
            }
    
    async def add_knowledge(self, documents: List[str], metadata: List[Dict]):
        """添加知识到数据库"""
        
        try:
            # 生成ID
            ids = [f"doc_{i}" for i in range(len(documents))]
            
            self.collection.add(
                documents=documents,
                metadatas=metadata,
                ids=ids
            )
            
            app_logger.info(f"添加了 {len(documents)} 条知识记录")
            
        except Exception as e:
            app_logger.error(f"添加知识失败: {e}")
            raise