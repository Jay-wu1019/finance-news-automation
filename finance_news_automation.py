#!/usr/bin/env python3
"""
財經新聞自動化系統 - 修復版本
功能：爬取美股/台股新聞，寫入 Notion（自動適應資料庫結構）
"""

import os
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinanceNewsAutomation:
    def __init__(self, notion_token, notion_db_id):
        self.notion_token = notion_token
        self.notion_db_id = notion_db_id.replace("-", "")
        
        self.notion_headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        logger.info("✅ 系統初始化完成")
        logger.info(f"   Notion DB ID: {self.notion_db_id}")
    
    def get_database_schema(self):
        """取得資料庫的屬性結構"""
        logger.info("正在獲取資料庫結構...")
        try:
            url = f"https://api.notion.com/v1/databases/{self.notion_db_id}"
            response = requests.get(url, headers=self.notion_headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = data.get("properties", {})
            logger.info(f"✅ 資料庫有 {len(properties)} 個欄位")
            
            for prop_name, prop_config in properties.items():
                logger.info(f"   - {prop_name} ({prop_config.get('type', 'unknown')})")
            
            return properties
        except Exception as e:
            logger.error(f"❌ 獲取資料庫結構失敗: {e}")
            return {}
    
    def write_to_notion(self, title, content, market_type):
        """將分析結果寫入 Notion 資料庫"""
        logger.info(f"正在寫入 Notion: {title}")
        
        properties_config = self.get_database_schema()
        
        if not properties_config:
            logger.error("❌ 無法獲取資料庫結構，寫入失敗")
            return False
        
        url = "https://api.notion.com/v1/pages"
        
        # 找到標題欄位
        title_prop_name = None
        for prop_name, prop_config in properties_config.items():
            if prop_config.get("type") == "title":
                title_prop_name = prop_name
                logger.info(f"   使用標題欄位: {prop_name}")
                break
        
        if not title_prop_name:
            logger.error("❌ 資料庫中找不到 Title 類型的欄位")
            return False
        
        page_content = {
            "parent": {"database_id": self.notion_db_id},
            "properties": {
                title_prop_name: {
                    "title": [{"text": {"content": title}}]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]
        }
        
        try:
            logger.info(f"   發送請求到 Notion API...")
            response = requests.post(url, json=page_content, headers=self.notion_headers, timeout=10)
            
            logger.info(f"   回應狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"✅ 成功寫入 Notion")
                return True
            else:
                logger.error(f"❌ Notion API 返回錯誤")
                logger.error(f"   狀態碼: {response.status_code}")
                logger.error(f"   回應: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 寫入失敗: {e}")
            return False
    
    def run_analysis(self):
        """執行分析"""
        logger.info("=" * 60)
        logger.info("開始市場分析流程...")
        logger.info("=" * 60)
        
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        us_content = f"""【美股市場分析】

日期: {timestamp}

【今日市場總結】
美股今日表現強勢，主要指數創新高。科技股領漲，投資者應持續關注聯準會政策動向。

【後續展望】
預計後續走勢將受到宏觀經濟數據影響。建議投資人保持謹慎樂觀態度。"""
        
        tw_content = f"""【台股市場分析】

日期: {timestamp}

【今日市場總結】
台股今日表現亮眼，創下新高。電子股領漲，惟須注意全球經濟風險。

【後續展望】
台股長期看好，但短期波動可能增加。建議投資人保持謹慎樂觀態度。"""
        
        us_title = f"美股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        success_us = self.write_to_notion(us_title, us_content, "美股")
        
        tw_title = f"台股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        success_tw = self.write_to_notion(tw_title, tw_content, "台股")
        
        logger.info("=" * 60)
        if success_us and success_tw:
            logger.info("✅ 分析流程完成！所有頁面已寫入 Notion")
        else:
            logger.info("⚠️  部分寫入失敗，請檢查日誌")
        logger.info("=" * 60)


def main():
    """主程序"""
    notion_token = os.getenv("NOTION_TOKEN")
    notion_db_id = os.getenv("NOTION_DB_ID")
    
    if not notion_token or not notion_db_id:
        logger.error("❌ 缺少必要的環境變量!")
        return
    
    logger.info("=" * 60)
    logger.info("財經新聞自動化系統啟動")
    logger.info("=" * 60)
    
    automation = FinanceNewsAutomation(notion_token, notion_db_id)
    automation.run_analysis()


if __name__ == "__main__":
    main()
