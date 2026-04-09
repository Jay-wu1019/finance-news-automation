#!/usr/bin/env python3
"""
財經新聞自動化爬蟲系統 v1.0
自動抓取 Yahoo股、鉅亨網、玩股網最新新聞
每天自動更新網站內容
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinanceNewsScraper:
    """財經新聞爬蟲"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.news_list = []
        logger.info("✅ 財經新聞爬蟲系統啟動")
    
    def scrape_yahoo_stock(self):
        """爬取 Yahoo 股市新聞"""
        logger.info("📊 正在爬取 Yahoo 股市新聞...")
        
        try:
            url = "https://tw.stock.yahoo.com/news"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 找新聞項目
            articles = soup.find_all('a', {'class': re.compile('.*news.*')})[:5]
            
            for article in articles:
                try:
                    title = article.get_text(strip=True)
                    link = article.get('href', '')
                    
                    if title and link:
                        if not link.startswith('http'):
                            link = 'https://tw.stock.yahoo.com' + link
                        
                        self.news_list.append({
                            'title': title,
                            'source': 'Yahoo股',
                            'source_url': link,
                            'type': '📰',
                            'category': '股市新聞'
                        })
                except Exception as e:
                    logger.warning(f"⚠️ 處理 Yahoo 文章失敗: {e}")
                    continue
            
            logger.info(f"✅ 成功獲取 {len(articles)} 則 Yahoo 股市新聞")
            
        except Exception as e:
            logger.error(f"❌ 爬取 Yahoo 股市失敗: {e}")
    
    def scrape_cnyes(self):
        """爬取 鉅亨網新聞"""
        logger.info("📊 正在爬取 鉅亨網新聞...")
        
        try:
            url = "https://news.cnyes.com/news/cat/tw_stock"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 找新聞項目
            articles = soup.find_all('a', {'class': re.compile('.*title.*')})[:5]
            
            for article in articles:
                try:
                    title = article.get_text(strip=True)
                    link = article.get('href', '')
                    
                    if title and link and len(title) > 5:
                        if not link.startswith('http'):
                            link = 'https://news.cnyes.com' + link
                        
                        self.news_list.append({
                            'title': title,
                            'source': '鉅亨網',
                            'source_url': link,
                            'type': '📰',
                            'category': '股市分析'
                        })
                except Exception as e:
                    logger.warning(f"⚠️ 處理鉅亨網文章失敗: {e}")
                    continue
            
            logger.info(f"✅ 成功獲取 {len(articles)} 則鉅亨網新聞")
            
        except Exception as e:
            logger.error(f"❌ 爬取鉅亨網失敗: {e}")
    
    def scrape_wantgoo(self):
        """爬取 玩股網新聞"""
        logger.info("📊 正在爬取 玩股網新聞...")
        
        try:
            url = "https://www.wantgoo.com/news"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 找新聞項目
            articles = soup.find_all('a', {'class': re.compile('.*news.*')})[:5]
            
            for article in articles:
                try:
                    title = article.get_text(strip=True)
                    link = article.get('href', '')
                    
                    if title and link and len(title) > 5:
                        if not link.startswith('http'):
                            link = 'https://www.wantgoo.com' + link
                        
                        self.news_list.append({
                            'title': title,
                            'source': '玩股網',
                            'source_url': link,
                            'type': '📰',
                            'category': '投資策略'
                        })
                except Exception as e:
                    logger.warning(f"⚠️ 處理玩股網文章失敗: {e}")
                    continue
            
            logger.info(f"✅ 成功獲取 {len(articles)} 則玩股網新聞")
            
        except Exception as e:
            logger.error(f"❌ 爬取玩股網失敗: {e}")
    
    def get_top_news(self, limit=5):
        """獲取排名前 5 的新聞"""
        # 排序並取前 5 個
        sorted_news = sorted(self.news_list, key=lambda x: x.get('title', ''))[:limit]
        return sorted_news
    
    def generate_html(self, news_list):
        """生成 HTML 內容"""
        
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 生成新聞卡片 HTML
        news_cards_html = ""
        for i, news in enumerate(news_list, 1):
            if i > 5:
                break
            
            news_cards_html += f"""
                <div class="news-card">
                    <div class="card-header">
                        <div class="card-number">{'①②③④⑤'[i-1]}</div>
                        <div>
                            <div class="card-title">{news['title'][:40]}...</div>
                            <div class="card-category">{news.get('category', '最新消息')}</div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="card-content">
                            {news['title']}
                        </div>
                        <ul class="card-highlights">
                            <li>最新市場消息</li>
                            <li>即時更新</li>
                            <li>專業分析</li>
                        </ul>
                        <div class="card-tags">
                            <span class="tag">台股</span>
                            <span class="tag">美股</span>
                            <span class="tag">即時</span>
                        </div>
                        <div class="card-source">
                            📰 來源：<a href="{news['source_url']}" target="_blank">{news['source']}</a>
                        </div>
                    </div>
                </div>
            """
        
        # 生成完整 HTML
        html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>市場動態 | 美股台股今日消息</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .banner {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 50px 40px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            position: relative;
        }}

        .banner h1 {{
            font-size: 2.8em;
            color: white;
            margin-bottom: 15px;
        }}

        .banner p {{
            font-size: 1.1em;
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
        }}

        .banner-buttons {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .banner-btn {{
            padding: 12px 25px;
            border: 2px solid white;
            background: rgba(255,255,255,0.1);
            color: white;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }}

        .banner-btn:hover {{
            background: white;
            color: #667eea;
            transform: scale(1.05);
        }}

        .theme-toggle {{
            position: absolute;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 2px solid white;
            background: rgba(255,255,255,0.2);
            cursor: pointer;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .section-title {{
            font-size: 1.8em;
            color: white;
            margin: 50px 0 30px 0;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 50px;
        }}

        .news-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }}

        .news-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}

        .card-header {{
            padding: 25px;
            color: white;
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .card-number {{
            font-size: 2.5em;
            font-weight: bold;
            min-width: 50px;
        }}

        .card-title {{
            font-size: 1.3em;
            font-weight: bold;
        }}

        .card-category {{
            font-size: 0.9em;
            opacity: 0.85;
            margin-top: 5px;
        }}

        .card-body {{
            padding: 20px 25px;
            background: #2d2d44;
            flex-grow: 1;
        }}

        .card-content {{
            color: #e0e0e0;
            line-height: 1.6;
            margin-bottom: 15px;
            font-size: 0.95em;
        }}

        .card-highlights {{
            list-style: none;
            margin: 15px 0;
        }}

        .card-highlights li {{
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
            color: #51cf66;
            font-size: 0.9em;
        }}

        .card-highlights li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            font-weight: bold;
        }}

        .card-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }}

        .tag {{
            display: inline-block;
            padding: 5px 12px;
            background: rgba(102, 126, 234, 0.3);
            border: 1px solid #667eea;
            border-radius: 15px;
            font-size: 0.8em;
            color: #a0c4ff;
        }}

        .card-source {{
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 12px;
            margin-top: 15px;
            font-size: 0.85em;
            color: #999;
        }}

        .card-source a {{
            color: #a0c4ff;
            text-decoration: none;
        }}

        .card-source a:hover {{
            color: #667eea;
            text-decoration: underline;
        }}

        .footer {{
            text-align: center;
            color: #999;
            margin-top: 50px;
            padding: 20px;
        }}

        .update-info {{
            background: rgba(102, 126, 234, 0.1);
            padding: 15px;
            border-radius: 8px;
            color: #a0c4ff;
            margin-top: 20px;
        }}

        @media (max-width: 768px) {{
            .banner h1 {{
                font-size: 2em;
            }}

            .news-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <button class="theme-toggle">🌙</button>
            <h1>📈 財經新聞自動化平台</h1>
            <p>台灣人必看的股市消息｜每日自動更新</p>
            <div class="banner-buttons">
                <button class="banner-btn" onclick="window.open('https://instagram.com/wu_wealth_lab')">📱 追蹤 Instagram: @wu_wealth_lab</button>
                <button class="banner-btn" onclick="alert('✅ 資料已自動更新')">⚡ 資時數據更新</button>
                <button class="banner-btn" onclick="alert('由 Yahoo股、鉅亨網、玩股網 + AI 驅動')">🤖 AI 驅動分析</button>
            </div>
        </div>

        <div>
            <div class="section-title">🔥 前五大台灣人最關注消息</div>
            <div class="news-grid">
                {news_cards_html}
            </div>
        </div>

        <div class="footer">
            <div class="update-info">
                ✅ 自動化系統已啟動<br>
                📊 數據來源：Yahoo股、鉅亨網、玩股網<br>
                🔄 每天自動更新<br>
                ⏰ 最後更新：{timestamp}
            </div>
        </div>
    </div>

    <script>
        console.log('✅ 自動化財經新聞網站已加載');
    </script>
</body>
</html>
"""
        
        return html_content
    
    def run(self):
        """運行爬蟲"""
        logger.info("\n" + "="*70)
        logger.info("🚀 開始抓取財經新聞")
        logger.info("="*70)
        
        # 抓取新聞
        self.scrape_yahoo_stock()
        self.scrape_cnyes()
        self.scrape_wantgoo()
        
        logger.info(f"\n✅ 總共獲取 {len(self.news_list)} 則新聞")
        
        # 獲取排名前 5
        top_news = self.get_top_news(5)
        
        # 生成 HTML
        html_content = self.generate_html(top_news)
        
        # 保存 HTML
        with open('market_news_auto.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("✅ HTML 文件已生成: market_news_auto.html")
        
        logger.info("\n" + "="*70)
        logger.info("🎉 財經新聞爬蟲完成！")
        logger.info("="*70)


if __name__ == "__main__":
    scraper = FinanceNewsScraper()
    scraper.run()
