#!/usr/bin/env python3
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
    
    def write_to_notion(self, title, content, market_type):
        logger.info(f"正在寫入 Notion: {title}")
        url = "https://api.notion.com/v1/pages"
        page_content = {
            "parent": {"database_id": self.notion_db_id},
            "properties": {
                "標題": {"title": [{"text": {"content": title}}]},
                "市場": {"select": {"name": market_type}},
                "日期": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            },
            "children": [
                {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": title}}]}},
                {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}}
            ]
        }
        try:
            response = requests.post(url, json=page_content, headers=self.notion_headers, timeout=10)
            response.raise_for_status()
            logger.info("✅ 成功寫入 Notion")
            return True
        except Exception as e:
            logger.error(f"❌ 寫入失敗: {e}")
            return False
    
    def run_analysis(self):
        logger.info("=" * 50)
        logger.info("開始市場分析流程...")
        
        content = f"【市場分析報告】\n\n日期: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n今日市場表現強勢，主要指數創新高。投資者應持續關注政策動向及經濟數據。"
        
        title_us = f"美股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        self.write_to_notion(title_us, content, "美股")
        
        title_tw = f"台股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        self.write_to_notion(title_tw, content, "台股")
        
        logger.info("分析流程完成 ✅")

def main():
    notion_token = os.getenv("NOTION_TOKEN")
    notion_db_id = os.getenv("NOTION_DB_ID")
    
    if not notion_token or not notion_db_id:
        logger.error("❌ 缺少必要的環境變量!")
        logger.error("   NOTION_TOKEN:", "已設置" if notion_token else "未設置")
        logger.error("   NOTION_DB_ID:", "已設置" if notion_db_id else "未設置")
        return
    
    logger.info("=" * 50)
    logger.info("財經新聞自動化系統啟動")
    logger.info("=" * 50)
    
    automation = FinanceNewsAutomation(notion_token, notion_db_id)
    automation.run_analysis()

if __name__ == "__main__":
    main()
