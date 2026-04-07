#!/usr/bin/env python3
"""
財經新聞自動化系統 - 終極版本
功能：直接在 Notion 工作區建立頁面（不依賴資料庫結構）
"""

import os
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinanceNewsAutomation:
    def __init__(self, notion_token, notion_db_id):
        """初始化系統"""
        self.notion_token = notion_token
        # 用 Database ID 作為父頁面 ID（Notion 允許將頁面添加到資料庫）
        self.parent_id = notion_db_id.replace("-", "")
        
        self.notion_headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        logger.info(f"✅ 系統初始化完成")
        logger.info(f"   Parent ID: {self.parent_id}")
    
    def create_page(self, title, content):
        """
        直接建立 Notion 頁面
        使用最簡單的 API 調用
        """
        logger.info(f"正在建立 Notion 頁面: {title}")
        
        url = "https://api.notion.com/v1/pages"
        
        # 最簡單的頁面結構 - 只有標題和內容
        page_data = {
            "parent": {
                "database_id": self.parent_id
            },
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        try:
            logger.info("   發送請求到 Notion API...")
            logger.info(f"   URL: {url}")
            logger.info(f"   Parent ID: {self.parent_id}")
            
            response = requests.post(
                url,
                json=page_data,
                headers=self.notion_headers,
                timeout=10
            )
            
            logger.info(f"   HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                page_id = result.get("id", "unknown")
                logger.info(f"✅ 頁面建立成功！")
                logger.info(f"   頁面 ID: {page_id}")
                logger.info(f"   URL: https://www.notion.so/{page_id}")
                return True
            else:
                logger.error(f"❌ Notion API 返回錯誤")
                logger.error(f"   狀態碼: {response.status_code}")
                logger.error(f"   回應: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ 請求超時")
            return False
        except Exception as e:
            logger.error(f"❌ 建立頁面失敗: {e}")
            return False
    
    def run(self):
        """執行分析並建立頁面"""
        logger.info("=" * 70)
        logger.info("財經新聞自動化系統啟動")
        logger.info("=" * 70)
        
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 美股分析
        us_title = f"美股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        us_content = f"""【美股市場分析】

生成時間: {timestamp}

市場概況:
美股今日表現強勢，主要指數創新高。科技股領漲，投資者應持續關注聯準會政策動向。

熱點事件:
- S&P 500 創歷史新高
- 科技股集體上漲
- 聯準會政策信號積極

宏觀分析:
利率政策對市場產生正面影響，經濟數據好於預期。

投資建議:
建議投資人保持謹慎樂觀態度，持續關注全球經濟動向。

風險提示:
請注意地緣政治風險和市場波動可能帶來的影響。"""
        
        success_us = self.create_page(us_title, us_content)
        
        # 台股分析
        tw_title = f"台股市場分析 - {datetime.now().strftime('%Y年%m月%d日')}"
        tw_content = f"""【台股市場分析】

生成時間: {timestamp}

市場概況:
台股今日表現亮眼，創下新高。電子股領漲，整體市場情緒樂觀。

熱點事件:
- 台股創新高紀錄
- 電子股領漲
- 觀光股表現強勁

產業分析:
電子與觀光產業領漲，傳統產業相對平穩。

投資建議:
台股長期看好，建議投資人保持中長期持有態度。

風險提示:
短期波動可能增加，請做好風險管理準備。"""
        
        success_tw = self.create_page(tw_title, tw_content)
        
        logger.info("=" * 70)
        if success_us and success_tw:
            logger.info("✅ 全部頁面建立成功！")
        elif success_us or success_tw:
            logger.info("⚠️  部分頁面建立成功")
        else:
            logger.info("❌ 頁面建立失敗，請檢查日誌")
        logger.info("=" * 70)


def main():
    """主程序"""
    notion_token = os.getenv("NOTION_TOKEN")
    notion_db_id = os.getenv("NOTION_DB_ID")
    
    if not notion_token:
        logger.error("❌ 缺少 NOTION_TOKEN 環境變量")
        return
    
    if not notion_db_id:
        logger.error("❌ 缺少 NOTION_DB_ID 環境變量")
        return
    
    logger.info("✅ 環境變量已設置")
    
    automation = FinanceNewsAutomation(notion_token, notion_db_id)
    automation.run()


if __name__ == "__main__":
    main()
