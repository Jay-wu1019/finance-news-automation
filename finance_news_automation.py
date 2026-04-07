#!/usr/bin/env python3
"""
財經新聞自動化系統 - 最終版本
支持資料庫和頁面雙重模式
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
        self.parent_id = notion_db_id.replace("-", "")
        
        self.notion_headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        logger.info(f"✅ 系統初始化")
        logger.info(f"   Parent ID: {self.parent_id}")
    
    def create_page_in_database(self, title, content):
        """在資料庫中建立頁面"""
        logger.info(f"方式1: 在資料庫中建立頁面 - {title}")
        
        url = "https://api.notion.com/v1/pages"
        
        page_data = {
            "parent": {"database_id": self.parent_id},
            "properties": {
                "title": {
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
            response = requests.post(url, json=page_data, headers=self.notion_headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ 方式1成功！")
                return True
            else:
                logger.warning(f"⚠️  方式1失敗 (HTTP {response.status_code})")
                return False
        except Exception as e:
            logger.warning(f"⚠️  方式1異常: {e}")
            return False
    
    def create_page_under_page(self, title, content):
        """在頁面下建立子頁面"""
        logger.info(f"方式2: 在頁面下建立子頁面 - {title}")
        
        url = "https://api.notion.com/v1/pages"
        
        page_data = {
            "parent": {"page_id": self.parent_id},
            "properties": {
                "title": {
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
            response = requests.post(url, json=page_data, headers=self.notion_headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ 方式2成功！")
                return True
            else:
                logger.warning(f"⚠️  方式2失敗 (HTTP {response.status_code})")
                return False
        except Exception as e:
            logger.warning(f"⚠️  方式2異常: {e}")
            return False
    
    def create_page(self, title, content):
        """嘗試多種方式建立頁面"""
        logger.info("=" * 60)
        logger.info(f"開始建立: {title}")
        
        success1 = self.create_page_in_database(title, content)
        
        if success1:
            return True
        
        logger.info("\n方式1失敗，嘗試方式2...")
        success2 = self.create_page_under_page(title, content)
        
        return success2
    
    def run(self):
        """執行"""
        logger.info("\n財經新聞自動化系統啟動\n")
        
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        us_title = f"美股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        us_content = f"""【美股市場分析】
生成時間: {timestamp}
美股今日表現強勢，主要指數創新高。科技股領漲。
建議持續關注聯準會政策動向。"""
        
        success_us = self.create_page(us_title, us_content)
        
        tw_title = f"台股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        tw_content = f"""【台股市場分析】
生成時間: {timestamp}
台股今日表現亮眼，創下新高。電子股領漲。
建議保持中長期持有態度。"""
        
        success_tw = self.create_page(tw_title, tw_content)
        
        logger.info("\n" + "=" * 60)
        if success_us and success_tw:
            logger.info("✅ 全部成功！")
        elif success_us or success_tw:
            logger.info("⚠️  部分成功")
        else:
            logger.info("❌ 全部失敗")


def main():
    notion_token = os.getenv("NOTION_TOKEN")
    notion_db_id = os.getenv("NOTION_DB_ID")
    
    if not notion_token or not notion_db_id:
        logger.error("❌ 缺少環境變量")
        return
    
    automation = FinanceNewsAutomation(notion_token, notion_db_id)
    automation.run()


if __name__ == "__main__":
    main()
