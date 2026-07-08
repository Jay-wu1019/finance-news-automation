#!/usr/bin/env python3
"""
財經新聞自動化系統
每日抓取台股/美股真實指數、個股數據與新聞，產生網站首頁 docs/index.html
"""

import html
import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_PATH = "docs/index.html"
TAIPEI_TZ = timezone(timedelta(hours=8))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

TW_NEWS_RSS = "https://tw.stock.yahoo.com/rss?category=tw-market"
US_NEWS_API = "https://api.cnyes.com/media/api/v1/newslist/category/us_stock?limit=6"
MAX_NEWS_ITEMS = 5

TW_INDEX = ("^TWII", "台股加權指數")
TW_WATCHLIST = [
    ("2330.TW", "台積電"),
    ("2317.TW", "鴻海"),
    ("2454.TW", "聯發科"),
    ("2308.TW", "台達電"),
    ("3008.TW", "大立光"),
    ("2603.TW", "長榮"),
    ("2882.TW", "國泰金"),
    ("1301.TW", "台塑"),
    ("2891.TW", "中信金"),
    ("2382.TW", "廣達"),
]

US_INDICES = [
    ("^DJI", "道瓊工業指數"),
    ("^GSPC", "標普500"),
    ("^IXIC", "那斯達克"),
    ("^SOX", "費城半導體"),
]
US_WATCHLIST = [
    ("AAPL", "蘋果"),
    ("MSFT", "微軟"),
    ("NVDA", "輝達"),
    ("TSLA", "特斯拉"),
    ("META", "Meta"),
    ("GOOGL", "Alphabet"),
    ("AMZN", "亞馬遜"),
    ("NFLX", "網飛"),
    ("INTC", "英特爾"),
    ("TSM", "台積電ADR"),
]


def fetch_quote(symbol, name):
    """透過 Yahoo Finance 公開圖表 API 取得即時報價"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = requests.get(url, headers=HEADERS, params={"interval": "1d", "range": "5d"}, timeout=15)
    response.raise_for_status()

    result = response.json()["chart"]["result"][0]
    price = result["meta"]["regularMarketPrice"]

    # meta.chartPreviousClose 指向查詢區間更早之前的收盤價，不是「前一天」，
    # 會導致漲跌%完全錯誤。改用每日收盤價序列的倒數第二筆，才是真正的前一交易日收盤。
    closes = [c for c in result["indicators"]["quote"][0]["close"] if c is not None]
    prev_close = closes[-2]
    change = price - prev_close
    change_pct = (change / prev_close * 100) if prev_close else 0.0

    return {
        "symbol": symbol,
        "name": name,
        "price": price,
        "change": change,
        "change_pct": change_pct,
    }


def fetch_quotes(symbol_list):
    quotes = []
    for symbol, name in symbol_list:
        try:
            quotes.append(fetch_quote(symbol, name))
        except Exception as e:
            logger.warning(f"跳過 {symbol}（{name}）：{e}")
    return quotes


def fetch_tw_news():
    """從 Yahoo奇摩股市 RSS 抓取台股新聞"""
    logger.info(f"正在抓取台股新聞：{TW_NEWS_RSS}")

    response = requests.get(TW_NEWS_RSS, headers=HEADERS, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = []

    for item in root.findall("./channel/item")[:MAX_NEWS_ITEMS]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date_raw = item.findtext("pubDate")

        if not title or not link:
            continue

        pub_date_display = ""
        if pub_date_raw:
            try:
                dt = parsedate_to_datetime(pub_date_raw).astimezone(TAIPEI_TZ)
                pub_date_display = dt.strftime("%m/%d %H:%M")
            except (TypeError, ValueError):
                pass

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date_display,
            "source": "Yahoo股市",
        })

    logger.info(f"成功取得 {len(items)} 則台股新聞")
    return items


def fetch_us_news():
    """從 鉅亨網 API 抓取美股新聞（中文）"""
    logger.info(f"正在抓取美股新聞：{US_NEWS_API}")

    response = requests.get(US_NEWS_API, headers=HEADERS, timeout=15)
    response.raise_for_status()

    data = response.json()
    items = []

    for item in data.get("items", {}).get("data", [])[:MAX_NEWS_ITEMS]:
        title = (item.get("title") or "").strip()
        news_id = item.get("newsId")

        if not title or not news_id:
            continue

        raw_content = item.get("content", "")
        plain_text = re.sub(r"<[^>]+>", "", html.unescape(raw_content)).strip()

        pub_date_display = ""
        publish_at = item.get("publishAt")
        if publish_at:
            dt = datetime.fromtimestamp(publish_at, tz=timezone.utc).astimezone(TAIPEI_TZ)
            pub_date_display = dt.strftime("%m/%d %H:%M")

        items.append({
            "title": title,
            "link": f"https://news.cnyes.com/news/id/{news_id}",
            "description": plain_text,
            "pub_date": pub_date_display,
            "source": "鉅亨網",
        })

    logger.info(f"成功取得 {len(items)} 則美股新聞")
    return items


def format_price(value, currency_symbol=""):
    return f"{currency_symbol}{value:,.2f}"


def render_index_cards(indices):
    cards = []
    for idx in indices:
        css_class = "up" if idx["change"] >= 0 else "down"
        arrow = "▲" if idx["change"] >= 0 else "▼"
        cards.append(f"""
                <div class="index-card {css_class}">
                    <h4>{html.escape(idx['name'])}</h4>
                    <div class="index-value">{format_price(idx['price'])}</div>
                    <div class="index-change">{arrow} {idx['change']:+.2f} ({idx['change_pct']:+.2f}%)</div>
                </div>""")
    return "".join(cards)


def render_stock_table(stocks, currency_symbol=""):
    if not stocks:
        return '<p class="empty">目前沒有可顯示的個股資料。</p>'

    ranked = sorted(stocks, key=lambda s: s["change_pct"], reverse=True)

    rows = []
    for s in ranked:
        css_class = "green" if s["change_pct"] >= 0 else "red"
        rows.append(f"""
                    <tr>
                        <td>{html.escape(s['name'])}</td>
                        <td>{html.escape(s['symbol'])}</td>
                        <td>{format_price(s['price'], currency_symbol)}</td>
                        <td class="{css_class}">{s['change_pct']:+.2f}%</td>
                    </tr>""")

    return f"""
            <table class="stock-table">
                <thead>
                    <tr><th>個股</th><th>代號</th><th>股價</th><th>漲跌幅</th></tr>
                </thead>
                <tbody>{''.join(rows)}
                </tbody>
            </table>"""


def render_news_cards(news_items, empty_message):
    if not news_items:
        return f'<p class="empty">{empty_message}</p>'

    cards = []
    for i, news in enumerate(news_items, 1):
        title = html.escape(news["title"])
        link = html.escape(news["link"])
        description = html.escape(news["description"])[:90]
        pub_date = html.escape(news["pub_date"])
        source = html.escape(news["source"])

        cards.append(f"""
                <a class="news-card" href="{link}" target="_blank" rel="noopener">
                    <div class="card-header">
                        <div class="card-number">{i:02d}</div>
                        <div class="card-title">{title}</div>
                    </div>
                    <div class="card-body">
                        <p class="card-desc">{description}</p>
                        <div class="card-meta">
                            <span>📰 {source}</span>
                            <span>{pub_date}</span>
                        </div>
                    </div>
                </a>""")

    return "".join(cards)


def render_html(tw_index, tw_stocks, us_indices, us_stocks, tw_news, us_news):
    timestamp = datetime.now(TAIPEI_TZ).strftime("%Y年%m月%d日 %H:%M")

    tw_index_html = render_index_cards([tw_index]) if tw_index else '<p class="empty">目前無法取得台股加權指數。</p>'
    us_index_html = render_index_cards(us_indices) if us_indices else '<p class="empty">目前無法取得美股指數。</p>'
    tw_table_html = render_stock_table(tw_stocks, currency_symbol="")
    us_table_html = render_stock_table(us_stocks, currency_symbol="$")
    tw_news_html = render_news_cards(tw_news, "目前沒有可顯示的台股新聞，請稍後再試。")
    us_news_html = render_news_cards(us_news, "目前沒有可顯示的美股新聞，請稍後再試。")

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>財經新聞自動化 | 台美股每日真實數據</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a3a52 0%, #2d5a7b 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1300px; margin: 0 auto; }}
        .banner {{
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            padding: 45px 40px;
            text-align: center;
            margin-bottom: 35px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .banner h1 {{ font-size: 2.3em; color: white; margin-bottom: 10px; }}
        .banner p {{ font-size: 1em; color: rgba(255,255,255,0.85); margin-bottom: 18px; }}
        .ig-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 10px 22px;
            border-radius: 25px;
        }}
        .ig-badge a {{ color: white; text-decoration: none; font-weight: bold; }}
        .ig-badge a:hover {{ text-decoration: underline; }}
        .info-box {{
            background: rgba(255,255,255,0.1);
            border-left: 4px solid #FF9800;
            padding: 18px 22px;
            margin-bottom: 30px;
            border-radius: 8px;
            color: #FFD54F;
            font-size: 0.95em;
        }}
        .section-title {{
            font-size: 1.6em;
            color: white;
            margin: 40px 0 20px 0;
            padding-left: 15px;
            border-left: 4px solid white;
        }}
        .index-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }}
        .index-card {{
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.2);
            border-left: 5px solid #999;
        }}
        .index-card.up {{ border-left-color: #2e7d32; }}
        .index-card.down {{ border-left-color: #c62828; }}
        .index-card h4 {{ color: #1a3a52; font-size: 0.85em; margin-bottom: 8px; }}
        .index-value {{ font-size: 1.6em; font-weight: bold; color: #222; }}
        .index-change {{ font-size: 0.95em; margin-top: 6px; color: #444; }}
        .stock-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            margin-bottom: 30px;
        }}
        .stock-table th {{
            background: #1a3a52;
            color: white;
            padding: 12px 16px;
            text-align: left;
            font-size: 0.88em;
        }}
        .stock-table td {{
            padding: 11px 16px;
            border-bottom: 1px solid #f0f0f0;
            color: #333;
            font-size: 0.92em;
        }}
        .stock-table tr:last-child td {{ border-bottom: none; }}
        .stock-table tr:hover td {{ background: #f8f9fa; }}
        .green {{ color: #2e7d32; font-weight: bold; }}
        .red {{ color: #c62828; font-weight: bold; }}
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .news-card {{
            display: block;
            background: #22405a;
            border-radius: 12px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            transition: transform 0.2s ease;
        }}
        .news-card:hover {{ transform: translateY(-4px); }}
        .card-header {{ display: flex; align-items: center; gap: 15px; padding: 18px 20px 10px 20px; }}
        .card-number {{ font-size: 1.5em; font-weight: bold; color: #90caf9; min-width: 36px; }}
        .card-title {{ font-size: 1.02em; font-weight: bold; color: white; line-height: 1.4; }}
        .card-body {{ padding: 0 20px 18px 20px; }}
        .card-desc {{ font-size: 0.88em; color: #c3d3e0; line-height: 1.5; margin-bottom: 12px; }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8em;
            color: #9ab;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 10px;
        }}
        .empty {{ color: #cbd; }}
        .footer {{ text-align: center; color: #cdd; margin-top: 40px; padding: 20px; }}
        .update-info {{
            background: rgba(255,255,255,0.08);
            padding: 15px;
            border-radius: 8px;
        }}
        @media (max-width: 768px) {{
            .banner h1 {{ font-size: 1.7em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <h1>📈 財經新聞自動化平台</h1>
            <p>台美股每日真實數據與新聞｜每日台灣時間下午 1:30 自動更新</p>
            <div class="ig-badge">
                <a href="https://instagram.com/wu_wealth_lab" target="_blank" rel="noopener">📱 追蹤 Instagram: @wu_wealth_lab</a>
            </div>
        </div>

        <div class="info-box">
            📊 更新時間：{timestamp}（台灣時間）｜資料來源：Yahoo Finance（指數/股價）、Yahoo股市與鉅亨網（新聞）
        </div>

        <div class="section-title">🇹🇼 台股市場</div>
        <div class="index-grid">{tw_index_html}
        </div>
        {tw_table_html}

        <div class="section-title">🇺🇸 美股市場</div>
        <div class="index-grid">{us_index_html}
        </div>
        {us_table_html}

        <div class="section-title">🔥 台股焦點新聞</div>
        <div class="news-grid">{tw_news_html}
        </div>

        <div class="section-title">🚀 美股焦點新聞</div>
        <div class="news-grid">{us_news_html}
        </div>

        <div class="footer">
            <div class="update-info">
                📊 指數與個股資料來源：Yahoo Finance｜新聞來源：Yahoo股市、鉅亨網<br>
                🔄 每天台灣時間下午 1:30 自動更新<br>
                ⏰ 最後更新：{timestamp}（台灣時間）<br>
                ⚠️ 本站僅提供公開市場數據與新聞彙整，不構成投資建議。
            </div>
        </div>
    </div>
</body>
</html>
"""


def main():
    tw_index_quotes = fetch_quotes([TW_INDEX])
    tw_index = tw_index_quotes[0] if tw_index_quotes else None
    tw_stocks = fetch_quotes(TW_WATCHLIST)

    us_indices = fetch_quotes(US_INDICES)
    us_stocks = fetch_quotes(US_WATCHLIST)

    try:
        tw_news = fetch_tw_news()
    except Exception as e:
        logger.warning(f"抓取台股新聞失敗：{e}")
        tw_news = []

    try:
        us_news = fetch_us_news()
    except Exception as e:
        logger.warning(f"抓取美股新聞失敗：{e}")
        us_news = []

    if not tw_index and not tw_stocks and not us_indices and not us_stocks and not tw_news and not us_news:
        logger.error("所有資料來源都失敗，保留現有頁面")
        sys.exit(1)

    html_content = render_html(tw_index, tw_stocks, us_indices, us_stocks, tw_news, us_news)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"✅ 已更新 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
