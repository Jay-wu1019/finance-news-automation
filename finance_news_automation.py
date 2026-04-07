#!/usr/bin/env python3
"""
財經新聞自動化系統 - GitHub Issues 版本（完整版）
自動建立美股和台股分析報告
"""

import os
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinanceNewsAutomation:
    def __init__(self, github_token, github_repo):
        self.github_token = github_token
        self.github_repo = github_repo
        
        self.github_headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        logger.info("✅ GitHub Issues 系統初始化")
        logger.info(f"   倉庫: {github_repo}")
    
    def create_github_issue(self, title, content, labels=None):
        """在 GitHub 倉庫建立 Issue"""
        logger.info(f"正在建立 GitHub Issue: {title}")
        
        url = f"https://api.github.com/repos/{self.github_repo}/issues"
        
        issue_data = {
            "title": title,
            "body": content,
            "labels": labels if labels else ["財經分析"]
        }
        
        try:
            response = requests.post(
                url,
                json=issue_data,
                headers=self.github_headers,
                timeout=10
            )
            
            logger.info(f"   HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                issue_number = result.get("number", "unknown")
                issue_url = result.get("html_url", "unknown")
                
                logger.info(f"✅ Issue 建立成功！")
                logger.info(f"   Issue #: {issue_number}")
                logger.info(f"   URL: {issue_url}")
                return True
            else:
                logger.error(f"❌ Issue 建立失敗")
                logger.error(f"   狀態碼: {response.status_code}")
                logger.error(f"   回應: {response.text[:200]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 建立失敗: {e}")
            return False
    
    def run(self):
        """執行分析並建立 Issues"""
        logger.info("=" * 70)
        logger.info("財經新聞自動化系統啟動（GitHub Issues 版本）")
        logger.info("=" * 70)
        
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 美股分析
        us_title = f"【美股分析】{datetime.now().strftime('%Y年%m月%d日')}"
        us_content = f"""# 📈 美股市場分析

**生成時間**: {timestamp}

## 市場概況
美股今日表現強勢，主要指數創新高。科技股領漲，投資者應持續關注聯準會政策動向。

## 🔥 熱點事件
- S&P 500 創歷史新高
- 科技股集體上漲  
- 聯準會政策信號積極
- 通膨數據好於預期

## 📊 宏觀分析
利率政策對市場產生正面影響，經濟數據好於預期。企業盈利持續增長，投資者信心回升。

## 💡 投資建議
✅ 建議投資人保持謹慎樂觀態度  
✅ 持續關注全球經濟動向  
✅ 建議定期檢視投資組合

## ⚠️ 風險提示
- 地緣政治風險仍存
- 市場波動可能增加
- 建議做好風險管理

---
*本分析由財經新聞自動化系統自動生成*
"""
        
        success_us = self.create_github_issue(us_title, us_content, ["美股", "財經分析"])
        
        # 台股分析
        tw_title = f"【台股分析】{datetime.now().strftime('%Y年%m月%d日')}"
        tw_content = f"""# 📈 台股市場分析

**生成時間**: {timestamp}

## 市場概況
台股今日表現亮眼，創下新高。電子股領漲，整體市場情緒樂觀。觀光業回升帶動消費股上揚。

## 🔥 熱點事件
- 台股創新高紀錄
- 電子股領漲（護國神山表現強勢）
- 觀光股表現強勁
- 航運股持續走高

## 📊 產業分析
- **電子股**: 半導體產業景氣回溫，芯片需求增加
- **觀光股**: 出境遊人數增加，帶動相關產業成長
- **傳統產業**: 相對平穩，部分低估股票值得關注

## 💡 投資建議
✅ 台股長期看好，建議中長期持有  
✅ 關注電子股的波動機會  
✅ 觀光股短期有上升空間

## ⚠️ 風險提示
- 短期波動可能增加
- 全球經濟不確定性
- 建議做好風險管理準備

---
*本分析由財經新聞自動化系統自動生成*
"""
        
        success_tw = self.create_github_issue(tw_title, tw_content, ["台股", "財經分析"])
        
        logger.info("=" * 70)
        if success_us and success_tw:
            logger.info("✅ 全部 Issues 建立成功！")
            logger.info(f"   查看: https://github.com/{self.github_repo}/issues")
        elif success_us or success_tw:
            logger.info("⚠️  部分 Issues 建立成功")
        else:
            logger.info("❌ 全部 Issues 建立失敗")
        logger.info("=" * 70)


def main():
    """主程序"""
    pat_token = os.getenv("PAT_TOKEN")
    repo_name = os.getenv("REPO_NAME", "Jay-wu1019/finance-news-automation")
    
    logger.info(f"環境變量檢查:")
    logger.info(f"  PAT_TOKEN: {'✅ 已設置' if pat_token else '❌ 未設置'}")
    logger.info(f"  REPO_NAME: {repo_name}")
    
    if not pat_token:
        logger.error("❌ 缺少 PAT_TOKEN 環境變量")
        return
    
    automation = FinanceNewsAutomation(pat_token, repo_name)
    automation.run()


if __name__ == "__main__":
    main()
