#!/usr/bin/env python3
"""
GitHub Issues 簡化測試版本
用於診斷 GitHub API 連接問題
"""

import os
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 環境變數檢查
    pat_token = os.getenv("PAT_TOKEN")
    repo_name = os.getenv("REPO_NAME", "Jay-wu1019/finance-news-automation")
    
    logger.info("=" * 70)
    logger.info("GitHub Issues 診斷工具 - 簡化版本")
    logger.info("=" * 70)
    
    logger.info(f"\n環境變數檢查:")
    logger.info(f"  PAT_TOKEN 已設置: {bool(pat_token)}")
    logger.info(f"  PAT_TOKEN 長度: {len(pat_token) if pat_token else 0}")
    logger.info(f"  REPO_NAME: {repo_name}")
    
    if not pat_token:
        logger.error("❌ PAT_TOKEN 未設置！")
        return
    
    # 準備 API 請求
    headers = {
        "Authorization": f"Bearer {pat_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    logger.info(f"\nAPI 頭設置:")
    logger.info(f"  Authorization: Bearer {pat_token[:20]}...")
    logger.info(f"  Accept: application/vnd.github.v3+json")
    logger.info(f"  Content-Type: application/json")
    
    # 建立一個簡單的 Issue
    url = f"https://api.github.com/repos/{repo_name}/issues"
    
    issue_data = {
        "title": f"【測試】GitHub API 連接 - {datetime.now().strftime('%H:%M:%S')}",
        "body": "這是一個測試 Issue，用於診斷 GitHub API 連接是否正常。",
        "labels": ["test"]
    }
    
    logger.info(f"\n準備建立 Issue:")
    logger.info(f"  URL: {url}")
    logger.info(f"  Title: {issue_data['title']}")
    logger.info(f"  Labels: {issue_data['labels']}")
    
    try:
        logger.info(f"\n正在發送 POST 請求...")
        response = requests.post(url, json=issue_data, headers=headers, timeout=10)
        
        logger.info(f"\n回應信息:")
        logger.info(f"  HTTP 狀態碼: {response.status_code}")
        logger.info(f"  Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 201:
            result = response.json()
            issue_number = result.get("number")
            issue_url = result.get("html_url")
            
            logger.info(f"\n✅ Issue 建立成功！")
            logger.info(f"  Issue #: {issue_number}")
            logger.info(f"  URL: {issue_url}")
        
        elif response.status_code == 401:
            logger.error(f"\n❌ 認證失敗 (HTTP 401)")
            logger.error(f"  可能原因：Token 無效或已過期")
            logger.error(f"  回應: {response.text[:500]}")
        
        elif response.status_code == 403:
            logger.error(f"\n❌ 權限不足 (HTTP 403)")
            logger.error(f"  可能原因：Token 沒有足夠的權限")
            logger.error(f"  回應: {response.text[:500]}")
        
        elif response.status_code == 404:
            logger.error(f"\n❌ 倉庫不存在 (HTTP 404)")
            logger.error(f"  可能原因：REPO_NAME 錯誤或倉庫無法訪問")
            logger.error(f"  REPO_NAME: {repo_name}")
            logger.error(f"  回應: {response.text[:500]}")
        
        else:
            logger.error(f"\n❌ 未知錯誤 (HTTP {response.status_code})")
            logger.error(f"  回應: {response.text[:500]}")
    
    except requests.exceptions.Timeout:
        logger.error(f"\n❌ 請求超時")
    except Exception as e:
        logger.error(f"\n❌ 異常: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("\n" + "=" * 70)
    logger.info("診斷完成")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
