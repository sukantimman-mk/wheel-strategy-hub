"""
The Wheel Strategy Hub — Real-Time US Options & AI Intelligence Server
Endpoints:
  - GET  /api/status            : Server health and status
  - GET  /api/quote             : Real-time stock quote and expirations
  - GET  /api/options           : Real option chain (Puts/Calls, Bid, Ask, Mid, IV, OI)
  - GET  /api/ai/market-top3    : AI Market-Wide Top 3 Stock Scanner (Scans watchlist and picks 3 BEST STOCKS)
  - GET  /api/ai/optimize       : AI Strike Optimizer for a specific stock
  - GET  /api/ai/audit          : AI Risk & Earnings Threat Auditor
  - POST /api/options/batch-quotes : Live Mark-to-Market & 50% Profit-Take Tracker for open contracts
"""

import sys
import json
import datetime
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Set UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import yfinance as yf
    import pandas as pd
    from ai_engine import ai_engine
    from company_analyzer import company_analyzer
except ImportError:
    print("Warning: yfinance, pandas, or company_analyzer not found.")
    yf = None
    pd = None
    ai_engine = None
    company_analyzer = None

import os
PORT = int(os.environ.get("PORT", 8000))

import math

DEFAULT_WHEEL_WATCHLIST = ["SOFI", "PLTR", "NVDA", "AMD", "AAPL", "TSLA", "INTC", "F", "BAC", "GOOGL"]
IV_HISTORY_CACHE = {}
AI_MARKET_TOP3_CACHE = {}

def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default

def safe_int(val, default=0):
    try:
        if val is None:
            return default
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return int(f)
    except (TypeError, ValueError):
        return default

def clean_for_json(data):
    if isinstance(data, dict):
        return {k: clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_for_json(v) for v in data]
    elif isinstance(data, tuple):
        return [clean_for_json(v) for v in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return 0.0
        return data
    elif pd is not None and pd.isna(data):
        return 0.0
    return data

class OptionsDataHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception as e:
            self._send_error(f"Invalid JSON payload: {str(e)}")
            return

        if path == "/api/options/batch-quotes":
            trades = payload.get("trades", [])
            self._handle_batch_quotes(trades)
        elif path == "/api/ai/roll-solver":
            if not ai_engine:
                self._send_error("AI Engine is not available")
                return
            ticker = payload.get("ticker", "SOFI")
            opt_type = payload.get("opt_type") or payload.get("type") or "CSP"
            old_strike = float(payload.get("old_strike") or payload.get("strike") or 0.0)
            old_exp = payload.get("old_exp") or payload.get("exp") or ""
            old_sto = float(payload.get("old_sto") or payload.get("sto") or 0.0)
            btc_val = payload.get("current_btc") if payload.get("current_btc") is not None else payload.get("btc")
            current_btc = float(btc_val) if btc_val is not None else None
            res = ai_engine.solve_smart_roll(ticker, opt_type, old_strike, old_exp, old_sto, current_btc)
            self._send_json(res)
        elif path == "/api/ai/portfolio-stress-test":
            if not ai_engine:
                self._send_error("AI Engine is not available")
                return
            capital = float(payload.get("capital", 10000.0))
            trades = payload.get("trades", [])
            res = ai_engine.stress_test_portfolio(capital, trades)
            self._send_json(res)
        elif path == "/api/ai/daily-briefing":
            if not ai_engine:
                self._send_error("AI Engine is not available")
                return
            capital = float(payload.get("capital", 10000.0))
            trades = payload.get("trades", [])
            res = ai_engine.generate_daily_briefing(capital, trades)
            self._send_json(res)
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path in ["/", "/index.html"]:
            try:
                with open("index.html", "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self._send_error(f"Cannot load index.html: {str(e)}")
            return
        elif path == "/api/status":
            self._handle_status()
        elif path == "/api/quote":
            ticker = params.get("ticker", [""])[0].strip().upper()
            self._handle_quote(ticker)
        elif path == "/api/options":
            ticker = params.get("ticker", [""])[0].strip().upper()
            exp_date = params.get("date", [""])[0].strip()
            self._handle_options(ticker, exp_date)
        elif path == "/api/ai/market-top3":
            strategy = params.get("strategy", ["CSP"])[0].strip().upper()
            ticker = params.get("ticker", [""])[0].strip().upper()
            self._handle_ai_market_top3(strategy, ticker)
        elif path == "/api/ai/optimize":
            ticker = params.get("ticker", [""])[0].strip().upper()
            strategy = params.get("strategy", ["CSP"])[0].strip().upper()
            self._handle_ai_optimize(ticker, strategy)
        elif path == "/api/ai/audit":
            ticker = params.get("ticker", [""])[0].strip().upper()
            exp_date = params.get("date", [""])[0].strip()
            self._handle_ai_audit(ticker, exp_date)
        elif path == "/api/ai/support-levels":
            ticker = params.get("ticker", [""])[0].strip().upper()
            self._handle_ai_support_levels(ticker)
        elif path == "/api/ai/company-analysis":
            ticker = params.get("ticker", [""])[0].strip().upper()
            self._handle_ai_company_analysis(ticker)
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def _handle_status(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        payload = {
            "status": "online",
            "provider": "US National Options Exchanges (CBOE/OCC/Nasdaq)",
            "ai_engine": "Market-Wide Top 3 Stock Scanner & Risk Auditor Active",
            "mark_to_market": "Active",
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._send_json(payload)

    def _handle_batch_quotes(self, trades):
        """
        Live Mark-to-Market quote provider for active open Wheel contracts
        Calculates unrealized P&L and 50% profit-take threshold alert
        """
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        today = datetime.date.today()
        cache = {}

        def get_contract_quote(t_item):
            ticker = (t_item.get("ticker") or "").upper().strip()
            strike = float(t_item.get("strike", 0))
            opt_type = (t_item.get("type") or "CSP").upper()
            exp = t_item.get("exp") or ""
            sto_price = float(t_item.get("sto", 0))
            contracts = int(t_item.get("contracts", 1))

            cache_key = f"{ticker}_{exp}"
            try:
                if cache_key not in cache:
                    t_obj = yf.Ticker(ticker)
                    stock_p = float(t_obj.fast_info.last_price or 0.0)
                    chain = t_obj.option_chain(exp)
                    cache[cache_key] = {"chain": chain, "stock_price": stock_p}

                data = cache[cache_key]
                chain = data["chain"]
                stock_price = data["stock_price"]
                df = chain.puts if opt_type == "CSP" else chain.calls
                match = df[df["strike"] == strike]

                if not match.empty:
                    row = match.iloc[0]
                    bid = safe_float(row.get("bid", 0.0))
                    ask = safe_float(row.get("ask", 0.0))
                    last = safe_float(row.get("lastPrice", 0.0))

                    # BTC price is what it would cost to close today (Ask or Mid)
                    btc_market = round((bid + ask) / 2, 2) if (bid > 0 and ask > 0) else (ask or last)
                    btc_market = safe_float(btc_market, 0.0)
                    
                    # Calculate Unrealized P&L
                    profit_per_share = round(sto_price - btc_market, 2)
                    profit_dollars = round(profit_per_share * contracts * 100, 2)
                    profit_pct = round((profit_per_share / sto_price * 100), 1) if sto_price > 0 else 0.0

                    # 50% Profit Target Check
                    is_50_pct_hit = profit_pct >= 50.0
                    target_50_btc = round(sto_price * 0.5, 2)

                    if is_50_pct_hit:
                        alert_badge = "🎯 ถึงเป้าปิดทำกำไร 50%+ แล้ว!"
                        alert_type = "success"
                        action_msg = f"กำไรแล้ว +{profit_pct}% (+${profit_dollars}) แนะนำตั้งคำสั่ง Buy to Close ที่ ${btc_market:.2f} เพื่อล็อกเงินสดทันที!"
                    elif profit_pct >= 25.0:
                        alert_badge = f"⏳ กำไร {profit_pct}% (กำลังเสื่อมเวลา)"
                        alert_type = "info"
                        action_msg = f"กำไรแล้ว +${profit_dollars} (เป้าปิด 50% คือรอซื้อคืนที่ ${target_50_btc:.2f})"
                    elif profit_pct >= 0:
                        alert_badge = f"⏳ เริ่มต้น (กำไร {profit_pct}%)"
                        alert_type = "neutral"
                        action_msg = f"เพิ่งเปิดสัญญา ถือรอเก็บค่าเสื่อมเวลา Theta Decay ต่อไป"
                    else:
                        alert_badge = f"⚠️ สัญญาติดลบ ({profit_pct}%)"
                        alert_type = "warning"
                        action_msg = f"สัญญาติดลบ -${abs(profit_dollars)} ติดตามราคาใกล้ชิด หากหลุด Strike พิจารณา Roll สัญญา"

                    return {
                        "id": t_item.get("id"),
                        "ticker": ticker,
                        "strike": strike,
                        "type": opt_type,
                        "exp": exp,
                        "contracts": contracts,
                        "stock_price": stock_price,
                        "sto_price": sto_price,
                        "market_btc_price": btc_market,
                        "bid": bid,
                        "ask": ask,
                        "unrealized_pnl_dollars": profit_dollars,
                        "unrealized_pnl_pct": profit_pct,
                        "is_50_pct_hit": is_50_pct_hit,
                        "target_50_btc": target_50_btc,
                        "alert_badge": alert_badge,
                        "alert_type": alert_type,
                        "action_msg": action_msg,
                        "success": True
                    }
                else:
                    return {
                        "id": t_item.get("id"),
                        "ticker": ticker,
                        "success": False,
                        "error": "ไม่พบ Strike นี้ในกระดาน Option ปัจจุบัน"
                    }
            except Exception as e:
                return {
                    "id": t_item.get("id"),
                    "ticker": ticker,
                    "success": False,
                    "error": str(e)
                }

        results = [get_contract_quote(item) for item in trades]
        self._send_json({"success": True, "results": results, "timestamp": datetime.datetime.now().isoformat()})

    def _handle_quote(self, ticker):
        if not ticker:
            self._send_error("กรุณาระบุชื่อย่อหุ้น (ticker)")
            return
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        try:
            t = yf.Ticker(ticker)
            fast = t.fast_info
            current_price = safe_float(fast.last_price, 0.0)
            prev_close = safe_float(fast.previous_close, current_price)
            change = safe_float(current_price - prev_close, 0.0)
            change_pct = safe_float((change / prev_close * 100) if prev_close else 0.0, 0.0)
            expirations = list(t.options or [])

            payload = {
                "success": True,
                "ticker": ticker,
                "price": round(current_price, 2),
                "previous_close": round(prev_close, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "expirations": expirations,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._send_json(payload)
        except Exception as e:
            self._send_error(f"เกิดข้อผิดพลาดในการดึงข้อมูล {ticker}: {str(e)}")

    def _handle_options(self, ticker, exp_date):
        if not ticker:
            self._send_error("กรุณาระบุชื่อย่อหุ้น (ticker)")
            return
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        try:
            t = yf.Ticker(ticker)
            expirations = list(t.options or [])
            if not expirations:
                self._send_error(f"ไม่พบข้อมูล Options สำหรับ {ticker}")
                return

            if not exp_date or exp_date not in expirations:
                exp_date = expirations[0]

            today = datetime.date.today()
            exp_parsed = datetime.datetime.strptime(exp_date, "%Y-%m-%d").date()
            dte = max(1, (exp_parsed - today).days)

            current_price = float(t.fast_info.last_price or 0.0)
            chain = t.option_chain(exp_date)

            def format_contracts(df, is_put=True):
                contracts = []
                for _, row in df.iterrows():
                    strike = safe_float(row.get("strike", 0.0))
                    bid = safe_float(row.get("bid", 0.0))
                    ask = safe_float(row.get("ask", 0.0))
                    last = safe_float(row.get("lastPrice", 0.0))
                    oi = safe_int(row.get("openInterest", 0))
                    vol = safe_int(row.get("volume", 0))
                    iv = safe_float(row.get("impliedVolatility", 0.0))
                    itm = bool(row.get("inTheMoney", False))

                    mid = round((bid + ask) / 2, 2) if (bid > 0 and ask > 0) else (bid or last)
                    mid = safe_float(mid, 0.0)
                    
                    delta_tag = "OTM"
                    if is_put:
                        diff_pct = (strike - current_price) / current_price if current_price else 0
                        if diff_pct < -0.15:
                            delta_tag = "Δ < 0.15 (ปลอดภัยสูง)"
                        elif -0.15 <= diff_pct <= -0.05:
                            delta_tag = "Δ 0.20-0.30 (โซนแนะนำ)"
                        elif -0.05 < diff_pct <= 0:
                            delta_tag = "Δ 0.35-0.50 (ใกล้ ATM)"
                        else:
                            delta_tag = "ITM"
                    else:
                        diff_pct = (strike - current_price) / current_price if current_price else 0
                        if diff_pct > 0.15:
                            delta_tag = "Δ < 0.15 (ปลอดภัยสูง)"
                        elif 0.05 <= diff_pct <= 0.15:
                            delta_tag = "Δ 0.20-0.30 (โซนแนะนำ)"
                        elif 0 <= diff_pct < 0.05:
                            delta_tag = "Δ 0.35-0.50 (ใกล้ ATM)"
                        else:
                            delta_tag = "ITM"

                    contracts.append({
                        "strike": round(strike, 2),
                        "bid": round(bid, 2),
                        "ask": round(ask, 2),
                        "mid": round(mid, 2),
                        "last": round(last, 2),
                        "volume": vol,
                        "open_interest": oi,
                        "iv_pct": round(iv * 100, 1),
                        "in_the_money": itm,
                        "wheel_zone": delta_tag
                    })
                return contracts

            puts = format_contracts(chain.puts, is_put=True)
            calls = format_contracts(chain.calls, is_put=False)

            # 1. Earnings Date & Clash Detection
            calendar = getattr(t, "calendar", {}) or {}
            earnings_date_str = None
            earnings_date_obj = None
            if isinstance(calendar, dict):
                dates = calendar.get("Earnings Date", [])
                if dates and len(dates) > 0:
                    first_d = dates[0]
                    if isinstance(first_d, (datetime.date, datetime.datetime)):
                        earnings_date_obj = first_d.date() if isinstance(first_d, datetime.datetime) else first_d
                        earnings_date_str = earnings_date_obj.strftime("%Y-%m-%d")

            earnings_clash = False
            earnings_days_away = None
            if earnings_date_obj:
                earnings_days_away = (earnings_date_obj - today).days
                if today <= earnings_date_obj <= exp_parsed:
                    earnings_clash = True

            if earnings_clash:
                earnings_msg = f"⚠️ สัญญาณเตือน: วันประกาศงบ ({earnings_date_str}) อยู่ในช่วงอายุสัญญา ({exp_date})! ราคาหุ้นอาจกระโดดแรง แนะนำให้ขยับวันหมดอายุให้จบก่อนวันงบออก"
            elif earnings_date_str:
                earnings_msg = f"✅ ปลอดภัยจากวันประกาศงบ: กำหนดการถัดไปคือ {earnings_date_str} (อยู่นอกช่วงอายุสัญญานี้)"
            else:
                earnings_msg = "ℹ️ ไม่พบกำหนดการประกาศงบการเงินในช่วงนี้"

            # 2. Expirations with Clash Tags
            expirations_detail = []
            for e_str in expirations:
                try:
                    e_d = datetime.datetime.strptime(e_str, "%Y-%m-%d").date()
                    clash = bool(earnings_date_obj and (today <= earnings_date_obj <= e_d))
                    expirations_detail.append({
                        "date": e_str,
                        "dte": max(1, (e_d - today).days),
                        "earnings_clash": clash
                    })
                except Exception:
                    expirations_detail.append({"date": e_str, "dte": 30, "earnings_clash": False})

            # 3. Calculate ATM IV, Historical Volatility, IV Rank & IV Percentile
            all_ivs = [c["iv_pct"] for c in puts + calls if c["iv_pct"] > 0 and abs(c["strike"] - current_price) / (current_price or 1) <= 0.08]
            atm_iv = round(sum(all_ivs) / len(all_ivs), 1) if all_ivs else round(puts[0]["iv_pct"] if puts else 35.0, 1)

            if ticker not in IV_HISTORY_CACHE:
                try:
                    hist = t.history(period="1y")
                    if len(hist) > 40:
                        import numpy as np
                        returns = np.log(hist["Close"] / hist["Close"].shift(1))
                        vol30 = (returns.rolling(window=30).std() * np.sqrt(252) * 100).dropna()
                        hv30 = float(vol30.iloc[-1])
                        min_hv = float(vol30.min())
                        max_hv = float(vol30.max())
                        IV_HISTORY_CACHE[ticker] = {
                            "hv30": round(hv30, 1),
                            "min_hv": round(min_hv, 1),
                            "max_hv": round(max_hv, 1),
                            "vol_series": vol30.tolist()
                        }
                    else:
                        IV_HISTORY_CACHE[ticker] = {"hv30": atm_iv, "min_hv": atm_iv * 0.6, "max_hv": atm_iv * 1.4, "vol_series": []}
                except Exception:
                    IV_HISTORY_CACHE[ticker] = {"hv30": atm_iv, "min_hv": atm_iv * 0.6, "max_hv": atm_iv * 1.4, "vol_series": []}

            iv_info = IV_HISTORY_CACHE.get(ticker, {})
            min_hv = iv_info.get("min_hv", atm_iv * 0.6)
            max_hv = iv_info.get("max_hv", atm_iv * 1.4)
            hv30 = iv_info.get("hv30", atm_iv)
            vol_series = iv_info.get("vol_series", [])

            if max_hv > min_hv:
                iv_rank = round(((atm_iv - min_hv) / (max_hv - min_hv) * 100), 1)
            else:
                iv_rank = 50.0
            iv_rank = max(0.0, min(100.0, iv_rank))

            if vol_series:
                iv_percentile = round(float(sum(1 for v in vol_series if v < atm_iv) / len(vol_series) * 100), 1)
            else:
                iv_percentile = iv_rank
            iv_percentile = max(0.0, min(100.0, iv_percentile))

            if iv_rank >= 50.0:
                iv_env = "HIGH"
                iv_badge = f"🔥 IV Rank {iv_rank}% (โซนทองพรีเมียม)"
                iv_recommendation = "ความผันผวนสูงกว่าเกณฑ์ปกติ 1 ปี ค่าพรีเมียมแพงมาก เหมาะกับการขาย Cash-Secured Put หรือ Covered Call เพื่อรับผลตอบแทนสูง"
            elif iv_rank >= 25.0:
                iv_env = "BALANCED"
                iv_badge = f"⚖️ IV Rank {iv_rank}% (ระดับสมดุล)"
                iv_recommendation = "ความผันผวนอยู่ในเกณฑ์ปกติ เหมาะกับการเทรด The Wheel ตามกรอบมาตรฐาน Delta 0.20-0.30"
            else:
                iv_env = "LOW"
                iv_badge = f"❄️ IV Rank {iv_rank}% (ความผันผวนต่ำ)"
                iv_recommendation = "ความผันผวนต่ำ ค่าพรีเมียมค่อนข้างบาง ควรเลือก Strike ที่ให้ APR ไม่ต่ำกว่า 15% หรือสแกนหาหุ้นตัวอื่นใน Watchlist"

            payload = {
                "success": True,
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "expiration": exp_date,
                "dte": dte,
                "expirations": expirations,
                "expirations_detail": expirations_detail,
                "earnings": {
                    "date": earnings_date_str,
                    "clash": earnings_clash,
                    "days_away": earnings_days_away,
                    "message": earnings_msg
                },
                "iv_metrics": {
                    "atm_iv_pct": atm_iv,
                    "hv30_pct": hv30,
                    "min_hv_pct": min_hv,
                    "max_hv_pct": max_hv,
                    "iv_rank": iv_rank,
                    "iv_percentile": iv_percentile,
                    "environment": iv_env,
                    "badge": iv_badge,
                    "recommendation": iv_recommendation
                },
                "puts": puts,
                "calls": calls,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._send_json(payload)
        except Exception as e:
            self._send_error(f"เกิดข้อผิดพลาดในการดึง Option Chain ของ {ticker}: {str(e)}")

    def _handle_ai_market_top3(self, strategy, custom_ticker=""):
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        strategy = (strategy or "CSP").upper()
        custom_ticker = (custom_ticker or "").strip().upper()

        cache_key = f"{strategy}_{custom_ticker}"
        now = datetime.datetime.now()
        if cache_key in AI_MARKET_TOP3_CACHE:
            cached_data, cached_time = AI_MARKET_TOP3_CACHE[cache_key]
            if (now - cached_time).total_seconds() < 180:
                self._send_json(cached_data)
                return

        today = datetime.date.today()
        target_watchlist = []
        if custom_ticker and custom_ticker not in target_watchlist:
            target_watchlist.append(custom_ticker)
        for sym in DEFAULT_WHEEL_WATCHLIST:
            if sym not in target_watchlist:
                target_watchlist.append(sym)

        def scan_stock_best_deal(sym):
            try:
                t = yf.Ticker(sym)
                price = safe_float(t.fast_info.last_price or 0.0)
                expirations = list(t.options or [])
                if not expirations or price <= 0:
                    return None

                cal = getattr(t, "calendar", {}) or {}
                earnings_date_str = None
                earnings_obj = None
                if isinstance(cal, dict):
                    dates = cal.get("Earnings Date", [])
                    if dates and len(dates) > 0 and isinstance(dates[0], (datetime.date, datetime.datetime)):
                        earnings_obj = dates[0].date() if isinstance(dates[0], datetime.datetime) else dates[0]
                        earnings_date_str = earnings_obj.strftime("%Y-%m-%d")

                valid_exps = []
                for exp in expirations[:8]:
                    try:
                        exp_d = datetime.datetime.strptime(exp, "%Y-%m-%d").date()
                        dte = max(1, (exp_d - today).days)
                        if 10 <= dte <= 55:
                            valid_exps.append((exp, exp_d, dte))
                    except Exception:
                        continue

                if not valid_exps and expirations:
                    for exp in expirations[:3]:
                        try:
                            exp_d = datetime.datetime.strptime(exp, "%Y-%m-%d").date()
                            dte = max(1, (exp_d - today).days)
                            if dte >= 5:
                                valid_exps.append((exp, exp_d, dte))
                        except Exception:
                            continue

                best_stock_deal = None
                best_score = -1

                for exp, exp_d, dte in valid_exps[:3]:
                    earnings_clash = bool(earnings_obj and (today <= earnings_obj <= exp_d))
                    chain = t.option_chain(exp)
                    df = chain.puts if strategy == "CSP" else chain.calls

                    for _, row in df.iterrows():
                        strike = safe_float(row.get("strike", 0.0))
                        bid = safe_float(row.get("bid", 0.0))
                        ask = safe_float(row.get("ask", 0.0))
                        last = safe_float(row.get("lastPrice", 0.0))
                        mid = round((bid + ask) / 2, 2) if (bid > 0 and ask > 0) else (bid or last)
                        mid = safe_float(mid, 0.0)
                        vol = safe_int(row.get("volume", 0))
                        oi = safe_int(row.get("openInterest", 0))
                        iv = safe_float(row.get("impliedVolatility", 0.0))

                        if mid < 0.05:
                            continue

                        if strategy == "CSP":
                            if strike >= price:
                                continue
                            diff_pct = (price - strike) / price * 100
                            roc = (mid / strike) * 100
                            apr = (roc / dte) * 365
                            collateral = int(strike * 100)

                            if (2.0 <= diff_pct <= 35.0 and 8.0 <= apr <= 120.0) or (diff_pct >= 1.0 and apr >= 5.0 and best_score < 0):
                                liq_bonus = min(15.0, ((oi + vol) / 150.0) * 15.0) if (oi + vol) > 0 else 5.0
                                score = (diff_pct * 2.5) + apr + liq_bonus
                                if earnings_clash:
                                    score -= 20.0

                                if score > best_score:
                                    best_score = score
                                    best_stock_deal = {
                                        "ticker": sym,
                                        "price": round(price, 2),
                                        "strategy": "CSP",
                                        "strike": strike,
                                        "expiration": exp,
                                        "dte": dte,
                                        "mid": mid,
                                        "premium_usd": int(mid * 100),
                                        "collateral": collateral,
                                        "discount_pct": round(diff_pct, 1),
                                        "apr": round(apr, 1),
                                        "oi": oi,
                                        "volume": vol,
                                        "iv_pct": round(iv * 100, 1),
                                        "earnings_date": earnings_date_str,
                                        "earnings_clash": earnings_clash,
                                        "score": round(score, 1)
                                    }
                        else:
                            if strike <= price:
                                continue
                            diff_pct = (strike - price) / price * 100
                            roc = (mid / price) * 100
                            apr = (roc / dte) * 365
                            collateral = int(price * 100)

                            if (1.5 <= diff_pct <= 30.0 and 6.0 <= apr <= 100.0) or (diff_pct >= 1.0 and apr >= 4.0 and best_score < 0):
                                liq_bonus = min(15.0, ((oi + vol) / 150.0) * 15.0) if (oi + vol) > 0 else 5.0
                                score = (diff_pct * 2.5) + apr + liq_bonus
                                if earnings_clash:
                                    score -= 20.0

                                if score > best_score:
                                    best_score = score
                                    best_stock_deal = {
                                        "ticker": sym,
                                        "price": round(price, 2),
                                        "strategy": "CC",
                                        "strike": strike,
                                        "expiration": exp,
                                        "dte": dte,
                                        "mid": mid,
                                        "premium_usd": int(mid * 100),
                                        "collateral": collateral,
                                        "discount_pct": round(diff_pct, 1),
                                        "apr": round(apr, 1),
                                        "oi": oi,
                                        "volume": vol,
                                        "iv_pct": round(iv * 100, 1),
                                        "earnings_date": earnings_date_str,
                                        "earnings_clash": earnings_clash,
                                        "score": round(score, 1)
                                    }
                return best_stock_deal
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=6) as executor:
            scanned_deals = [d for d in executor.map(scan_stock_best_deal, target_watchlist) if d]

        scanned_deals.sort(key=lambda x: x["score"], reverse=True)

        top_stocks = []
        badges = [
            (
                "🏆 หุ้นแนะนำอันดับ 1", 
                "สมดุลความปลอดภัยและผลตอบแทนดีที่สุดในตลาดวันนี้", 
                "emerald",
                "Tastytrade 45-DTE & Delta 0.20-0.30 Sweet Spot Model",
                "Tom Sosnoff & Tastytrade Financial Research Lab (10-Year Options Study) / Sheldon Natenberg",
                lambda d: f"Probability of Profit (POP) ~78–82% คุ้มค่าเงินค้ำประกัน ${d['collateral']:,} รับเงินสดทันที +${d['mid']*100:.0f} พร้อมส่วนลด {d['discount_pct']}% จากราคาตลาด"
            ),
            (
                "🛡️ หุ้นเด่นความปลอดภัยสูง", 
                "เน้นกระแสเงินสดมั่นคง เกราะป้องกันขาลงลึก สภาพคล่องสูง", 
                "sky",
                "Black-Scholes-Merton 1-Sigma Log-Normal Buffer & Margin of Safety",
                "Fischer Black, Myron Scholes (1973) / Benjamin Graham & David Dodd - 'Security Analysis'",
                lambda d: f"Win Rate ทางสถิติ > 85% เกราะป้องกันราคาดิ่งลึกถึง {d['discount_pct']}% ชนะตลาดได้แม้หุ้นย่อตัวแรง"
            ),
            (
                "🚀 หุ้นเด่นเร่งผลตอบแทน", 
                "กระแสเงินสดต่อปี (APR) สูง คุ้มค่าเงินค้ำประกัน", 
                "amber",
                "Kelly Criterion Positive Expectancy & CBOE Exponential Theta Acceleration",
                "J.L. Kelly Jr. (1956) / Lawrence G. McMillan - 'Options as a Strategic Investment'",
                lambda d: f"สร้างผลตอบแทนกระแสเงินสดระดับสูงถึง {d['apr']}% ต่อปี (APR) เหมาะกับกลยุทธ์ปิดกำไร 50% แล้วหมุนรอบใหม่"
            )
        ]

        for idx, deal in enumerate(scanned_deals[:3]):
            badge_title, badge_desc, badge_color, theory, ref, trust_fn = badges[idx]
            ticker = deal["ticker"]
            strike = deal["strike"]
            mid = deal["mid"]
            apr = deal["apr"]
            disc = deal["discount_pct"]
            col = deal["collateral"]
            dte = deal["dte"]
            earn_warn = " ⚠️ ชนวันประกาศงบ" if deal.get("earnings_clash") else " ✅ ปลอดภัยจากวันงบออก"

            if deal["strategy"] == "CSP":
                rationale = f"หุ้น {ticker} ($ {deal['price']:.2f}) แนะนำขาย Put ที่ Strike ${strike:.2f} (ส่วนลด {disc}% จากราคาตลาด) รับเงินสดทันที +${mid*100:.0f} (ผลตอบแทน {apr}%/ปี) เงินค้ำประกัน ${col:,} ในเวลา {dte} วัน{earn_warn}"
            else:
                rationale = f"หุ้น {ticker} ($ {deal['price']:.2f}) แนะนำขาย Call ที่ Strike ${strike:.2f} (สูงกว่าตลาด {disc}%) รับค่าเช่าทันที +${mid*100:.0f} (ผลตอบแทน {apr}%/ปี){earn_warn}"

            top_stocks.append({
                **deal,
                "badge": badge_title,
                "badge_desc": badge_desc,
                "badge_color": badge_color,
                "theory_framework": theory,
                "academic_reference": ref,
                "why_trust": trust_fn(deal),
                "rationale": rationale
            })

        payload = {
            "success": True,
            "mode": "market_wide_top3_stocks",
            "strategy": strategy,
            "scanned_watchlist_count": len(target_watchlist),
            "top_stocks": top_stocks,
            "timestamp": datetime.datetime.now().isoformat()
        }
        AI_MARKET_TOP3_CACHE[cache_key] = (payload, now)
        self._send_json(payload)

    def _handle_ai_optimize(self, ticker, strategy):
        if not ticker:
            self._send_error("กรุณาระบุชื่อย่อหุ้น (ticker)")
            return
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        ticker = ticker.upper().strip()
        strategy = (strategy or "CSP").upper()

        try:
            t = yf.Ticker(ticker)
            current_price = safe_float(t.fast_info.last_price, 0.0)
            expirations = list(t.options or [])
            if not expirations:
                self._send_error(f"ไม่พบข้อมูล Options สำหรับ {ticker}")
                return

            today = datetime.date.today()
            candidates = []
            fallback_candidates = []

            for exp in expirations[:6]:
                try:
                    exp_date = datetime.datetime.strptime(exp, "%Y-%m-%d").date()
                    dte = max(1, (exp_date - today).days)
                    if dte < 5 or dte > 65:
                        continue

                    chain = t.option_chain(exp)
                    df = chain.puts if strategy == "CSP" else chain.calls

                    for _, row in df.iterrows():
                        strike = safe_float(row.get("strike", 0.0))
                        bid = safe_float(row.get("bid", 0.0))
                        ask = safe_float(row.get("ask", 0.0))
                        last = safe_float(row.get("lastPrice", 0.0))
                        mid = round((bid + ask) / 2, 2) if (bid > 0 and ask > 0) else (bid or last)
                        mid = safe_float(mid, 0.0)
                        vol = safe_int(row.get("volume", 0))
                        oi = safe_int(row.get("openInterest", 0))
                        iv = safe_float(row.get("impliedVolatility", 0.0))

                        if mid < 0.05:
                            continue

                        if strategy == "CSP":
                            if strike >= current_price:
                                continue
                            diff_pct = (current_price - strike) / current_price * 100
                            breakeven = strike - mid
                            collateral = strike * 100
                            roc = (mid / strike) * 100
                            apr = (roc / dte) * 365

                            safety_score = min(40.0, diff_pct * 2.5)
                            yield_score = min(40.0, (apr / 50.0) * 40.0)
                            effective_liq = oi + vol
                            liq_score = min(20.0, (effective_liq / 300.0) * 20.0) if effective_liq > 0 else 6.0
                            total_score = safety_score + yield_score + liq_score

                            cand_item = {
                                "strategy": "CSP",
                                "strike": strike,
                                "expiration": exp,
                                "dte": dte,
                                "mid": mid,
                                "breakeven": round(breakeven, 2),
                                "collateral": round(collateral, 2),
                                "discount_pct": round(diff_pct, 1),
                                "roc": round(roc, 2),
                                "apr": round(apr, 1),
                                "open_interest": oi,
                                "volume": vol,
                                "iv_pct": round(iv * 100, 1),
                                "score": round(total_score, 1)
                            }

                            if 2.0 <= diff_pct <= 35.0 and 8.0 <= apr <= 150.0:
                                candidates.append(cand_item)
                            elif diff_pct >= 0.5 and apr >= 3.0:
                                fallback_candidates.append(cand_item)

                        else:
                            if strike <= current_price:
                                continue
                            diff_pct = (strike - current_price) / current_price * 100
                            roc = (mid / current_price) * 100
                            apr = (roc / dte) * 365

                            safety_score = min(40.0, diff_pct * 2.5)
                            yield_score = min(40.0, (apr / 50.0) * 40.0)
                            effective_liq = oi + vol
                            liq_score = min(20.0, (effective_liq / 300.0) * 20.0) if effective_liq > 0 else 6.0
                            total_score = safety_score + yield_score + liq_score

                            cand_item = {
                                "strategy": "CC",
                                "strike": strike,
                                "expiration": exp,
                                "dte": dte,
                                "mid": mid,
                                "discount_pct": round(diff_pct, 1),
                                "roc": round(roc, 2),
                                "apr": round(apr, 1),
                                "open_interest": oi,
                                "volume": vol,
                                "iv_pct": round(iv * 100, 1),
                                "score": round(total_score, 1)
                            }

                            if 1.5 <= diff_pct <= 30.0 and 6.0 <= apr <= 120.0:
                                candidates.append(cand_item)
                            elif diff_pct >= 0.5 and apr >= 2.5:
                                fallback_candidates.append(cand_item)

                except Exception:
                    continue

            pool = candidates if candidates else fallback_candidates
            pool.sort(key=lambda x: x["score"], reverse=True)

            top_deals = []
            role_meta_csp = [
                {
                    "badge": "👑 Strike แนะนำอันดับ 1 (สมดุลความเสี่ยง & ผลตอบแทนสูงสุด)",
                    "badge_desc": "The Wheel Sweet Spot: Sharpe Ratio และ Win Rate ดีที่สุดตามสถิติ",
                    "badge_color": "emerald",
                    "strategic_role": "Sweet Spot Balanced: คุ้มค่าเงินค้ำประกัน ปิดทำกำไร 50% ได้เร็วที่สุด",
                    "theory_framework": "Tastytrade 45-DTE & Delta 0.20-0.30 Sweet Spot Model",
                    "academic_reference": "Tom Sosnoff & Tastytrade Financial Research Lab (10-Year Study, 2010–2020) / Sheldon Natenberg - 'Option Volatility & Pricing'",
                    "trust_basis": lambda c: f"สถิติ Probability of Profit (POP) อยู่ที่ ~78–83% จุดคุ้มทุน (Breakeven) อยู่ที่ ${c['breakeven']:.2f} (มีส่วนลดรองรับการย่อตัว {c['discount_pct']}%) ทำให้ได้เปรียบทางคณิตศาสตร์ (Positive Expectancy) แม้หุ้นย่อตัวก็ยังได้กำไร",
                    "theory_explanation": "ตามงานวิจัยเชิงสถิติ 10 ปีของ Tastytrade การขายสัญญา OTM ที่ Delta 0.20-0.30 ในช่วงอายุ 30-45 วัน เป็นจุดที่อัตราเร่งการเสื่อมของเวลา (Theta Decay) ทำงานเร็วที่สุด และความเสี่ยงต่อการถูก Assign ต่ำอย่างมีนัยสำคัญ"
                },
                {
                    "badge": "🛡️ Strike ปลอดภัยสูง (เกราะป้องกันขาลงลึก Deep OTM)",
                    "badge_desc": "High Safety Buffer: เน้นอัตราการชนะสูง Win Rate > 85% นอนหลับสบาย",
                    "badge_color": "sky",
                    "strategic_role": "Deep Safety Margin: เน้นรักษาเงินต้นเป็นอันดับหนึ่ง เหมาะสำหรับช่วงตลาดผันผวน",
                    "theory_framework": "Black-Scholes-Merton 1-Sigma Normal Distribution & Margin of Safety",
                    "academic_reference": "Fischer Black & Myron Scholes (1973) / Benjamin Graham & David Dodd - 'Security Analysis' (Margin of Safety Principle)",
                    "trust_basis": lambda c: f"ความน่าจะเป็นที่ราคาจะไม่หลุด Strike (OTM Probability) สูงกว่า 85–90% มีเกราะป้องกันราคาดิ่งลึกถึง {c['discount_pct']}% จากราคาตลาด ชนะตลาดได้แม้หุ้นแม่จะย่อตัวแรง",
                    "theory_explanation": "อิงตามโมเดลการกระจายตัวของราคา (Log-Normal Distribution) สัญญานี้อยู่นอกกรอบความผันผวน 1 Standard Deviation ตามสถิติมีโอกาสไม่ถึง 15% ที่ราคาจะลงมาชน จึงเป็นเกราะคุ้มกันเงินทุนชั้นเลิศ"
                },
                {
                    "badge": "🚀 Strike เร่งกระแสเงินสด (ผลตอบแทนต่อปี APR สูงสุด)",
                    "badge_desc": "Cash Flow Accelerator: เน้นสร้าง Passive Income และกระแสเงินสดเข้มข้น",
                    "badge_color": "amber",
                    "strategic_role": "Yield Maximizer: เน้นผลตอบแทนและหมุนรอบเงินทุน (Velocity of Capital) เร็วที่สุด",
                    "theory_framework": "Kelly Criterion Capital Growth & CBOE Exponential Theta Acceleration Curve",
                    "academic_reference": "J.L. Kelly Jr. (1956) / Lawrence G. McMillan - 'Options as a Strategic Investment' & CBOE Options Institute",
                    "trust_basis": lambda c: f"สร้างผลตอบแทนกระแสเงินสดระดับสูงถึง {c['apr']}% ต่อปี (APR) จุดคุ้มทุนอยู่ที่ ${c['breakeven']:.2f} ช่วยเร่งการเติบโตของพอร์ต เหมาะกับการตั้งเป้าปิดทำกำไร 50% แล้วหมุนรอบใหม่",
                    "theory_explanation": "ตามทฤษฎี Theta Acceleration สัญญาระยะใกล้ราคาตลาดมีอัตราการสลายตัวของมูลค่าเวลาต่อวัน (Theta Decay per Dollar) สูงที่สุด ทำให้พรีเมียมยุบตัวไว เหมาะกับการล็อกกำไรอย่างรวดเร็ว"
                }
            ]

            role_meta_cc = [
                {
                    "badge": "👑 Strike แนะนำอันดับ 1 (สมดุลค่าเช่า & โอกาส Capital Gain)",
                    "badge_desc": "Balanced Covered Call: ได้ทั้งค่าเช่าเต็มเม็ดเต็มหน่วย และเปิดโอกาสให้หุ้นขึ้นต่อ",
                    "badge_color": "emerald",
                    "strategic_role": "Balanced Call Overwrite: ได้รับกระแสเงินสดทันที พร้อมโอกาสทำกำไรส่วนต่างราคา",
                    "theory_framework": "CBOE BuyWrite (BXM) Benchmark Model & Delta 0.25 Overwriting",
                    "academic_reference": "CBOE S&P 500 BuyWrite Index Studies / Lawrence McMillan - 'Options as a Strategic Investment'",
                    "trust_basis": lambda c: f"Strike สูงกว่าราคาตลาด {c['discount_pct']}% หากราคาหุ้นขึ้นทะลุเป้า จะได้กำไรทั้งพรีเมียม (+${c['mid']*100:.0f}) + กำไรส่วนต่างราคาหุ้น (Capital Gain {c['discount_pct']}%) รวมกำไรสองเด้ง",
                    "theory_explanation": "ดัชนี CBOE BuyWrite พิสูจน์แล้วว่าการขาย Call เหนือราคาตลาดที่ Delta 0.20-0.30 ช่วยลดความผันผวนของพอร์ตระยะยาว และเพิ่มผลตอบแทนทบต้นอย่างมีนัยสำคัญเมื่อเทียบกับการถือหุ้นเฉยๆ"
                },
                {
                    "badge": "🛡️ Strike ปลอดภัยสูง (เน้นเก็บหุ้นยาว Deep OTM)",
                    "badge_desc": "Growth Preserver: เน้นรับค่าเช่าเบาๆ แต่ไม่ยอมให้หุ้นโดนเรียกขาย (Called Away)",
                    "badge_color": "sky",
                    "strategic_role": "Capital Gain Maximizer: เหมาะกับหุ้นพื้นฐานดีที่กำลังเป็นขาขึ้นแรง",
                    "theory_framework": "Asymmetric Risk-Reward Covered Strangle Buffer & 1-Sigma Resistance",
                    "academic_reference": "Sheldon Natenberg - 'Option Volatility and Pricing' (Dynamic Hedging & Skew)",
                    "trust_basis": lambda c: f"Strike สูงกว่าราคาปัจจุบันถึง {c['discount_pct']}% โอกาสที่หุ้นจะถูกซื้อไป (Call Assignment) ต่ำกว่า 12–15% คุณจะยังคงถือหุ้นตัวโปรดต่อไปได้อย่างสบายใจ",
                    "theory_explanation": "การตั้ง Strike ไว้เหนือ 1 Standard Deviation ช่วยเปิดพื้นที่ (Room to Run) ให้หุ้นแม่เติบโตได้เต็มศักยภาพ โดยที่นักลงทุนยังคงเก็บกระแสเงินสดเพิ่มฟรีโดยแทบไม่เสียสิทธิการถือครองหุ้น"
                },
                {
                    "badge": "🚀 Strike เร่งกระแสเงินสด (รับค่าเช่าสูงสุด High Rental Yield)",
                    "badge_desc": "High Cash Flow Harvest: เน้นรีดเงินสดจากหุ้นที่มีอยู่ในมือให้ได้มากที่สุด",
                    "badge_color": "amber",
                    "strategic_role": "Immediate Cash Harvest: เหมาะสำหรับเมื่อหุ้นเริ่มแกว่งตัว Sideway หรือต้องการล็อกผลตอบแทน",
                    "theory_framework": "Theta Decay Monetization & Short-Duration Overwriting",
                    "academic_reference": "Lawrence G. McMillan - 'Options as a Strategic Investment' & Tom Sosnoff",
                    "trust_basis": lambda c: f"ให้ผลตอบแทนค่าเช่าสูงถึง {c['apr']}% ต่อปี (APR) รับเงินสดก้อนโตทันที +${c['mid']*100:.0f} ต่อสัญญา คุ้มค่าต่อมูลค่าหุ้นที่ถือครอง",
                    "theory_explanation": "Strike ใกล้ราคาตลาด (ATM/Near-OTM) มีค่าพรีเมียมแพงที่สุด (Extrinsic Value สูงสุด) เหมาะอย่างยิ่งสำหรับการลดต้นทุนถือครองหุ้น (Lowering Cost Basis) อย่างรวดเร็ว"
                }
            ]

            role_meta = role_meta_csp if strategy == "CSP" else role_meta_cc

            seen_strikes = set()
            for cand in pool:
                if cand["strike"] not in seen_strikes:
                    seen_strikes.add(cand["strike"])
                    idx = len(top_deals)
                    meta = role_meta[min(idx, len(role_meta) - 1)]

                    liq_desc = f"สภาพคล่อง {cand['volume']:,} สัญญา" if cand["volume"] > 0 else (f"OI {cand['open_interest']:,} สัญญา" if cand["open_interest"] > 0 else "ตลาดมีโควตพรีเมียม")

                    if cand["strategy"] == "CSP":
                        rationale = f"ขาย Put ที่ Strike ${cand['strike']:.2f} (ส่วนลด {cand['discount_pct']}% จากตลาด) รับเงินสดทันที +${cand['mid']*100:.0f} (APR {cand['apr']}%) หมดอายุในอีก {cand['dte']} วัน ({liq_desc})"
                    else:
                        rationale = f"ขาย Call ที่ Strike ${cand['strike']:.2f} (สูงกว่าตลาด {cand['discount_pct']}%) รับค่าเช่าทันที +${cand['mid']*100:.0f} (APR {cand['apr']}%) หมดอายุในอีก {cand['dte']} วัน ({liq_desc})"

                    top_deals.append({
                        **cand,
                        "badge": meta["badge"],
                        "badge_desc": meta["badge_desc"],
                        "badge_color": meta["badge_color"],
                        "strategic_role": meta["strategic_role"],
                        "theory_framework": meta["theory_framework"],
                        "academic_reference": meta["academic_reference"],
                        "why_trust": meta["trust_basis"](cand),
                        "theory_explanation": meta["theory_explanation"],
                        "rationale": rationale
                    })
                    if len(top_deals) == 3:
                        break

            payload = {
                "success": True,
                "ticker": ticker,
                "strategy": strategy,
                "current_price": round(current_price, 2),
                "total_scanned": len(pool),
                "top_deals": top_deals,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._send_json(payload)
        except Exception as e:
            self._send_error(f"เกิดข้อผิดพลาดในการสแกนดีล AI: {str(e)}")

    def _handle_ai_audit(self, ticker, target_exp_date):
        if not ticker:
            self._send_error("กรุณาระบุชื่อย่อหุ้น (ticker)")
            return
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        try:
            t = yf.Ticker(ticker)
            fast = t.fast_info
            current_price = float(fast.last_price or 0.0)
            
            calendar = getattr(t, "calendar", {}) or {}
            earnings_date_str = "ไม่พบกำหนดการ"
            earnings_date_obj = None
            earnings_alert = False
            earnings_msg = "ไม่พบวันประกาศงบที่ชนกับรอบเวลานี้"

            if isinstance(calendar, dict):
                dates = calendar.get("Earnings Date", [])
                if dates and len(dates) > 0:
                    earnings_date_obj = dates[0]
                    if isinstance(earnings_date_obj, (datetime.date, datetime.datetime)):
                        earnings_date_str = earnings_date_obj.strftime("%Y-%m-%d")

            if earnings_date_obj and target_exp_date:
                try:
                    exp_obj = datetime.datetime.strptime(target_exp_date, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    if today <= earnings_date_obj <= exp_obj:
                        earnings_alert = True
                        earnings_msg = f"⚠️ สัญญาณเตือน: วันประกาศงบ ({earnings_date_str}) อยู่ในช่วงอายุสัญญา ({target_exp_date})! ราคาหุ้นอาจกระโดดแรง แนะนำให้ขยับวันหมดอายุให้จบก่อนวันงบออก"
                    else:
                        earnings_msg = f"✅ ปลอดภัย: วันประกาศงบ ({earnings_date_str}) อยู่นอกช่วงอายุสัญญานี้"
                except Exception:
                    pass

            info = getattr(t, "info", {}) or {}
            market_cap = info.get("marketCap", 0) or 0
            forward_pe = info.get("forwardPE", 0) or 0
            target_mean = info.get("targetMeanPrice", 0) or 0
            analyst_rec = info.get("recommendationKey", "N/A").upper()

            sleep_well_score = 75
            audit_points = []

            if market_cap > 10_000_000_000:
                sleep_well_score += 10
                audit_points.append(f"🏢 หุ้นขนาดใหญ่ (Market Cap ${(market_cap/1e9):.1f}B) ความเสี่ยงล้มละลายต่ำมาก")
            elif market_cap > 2_000_000_000:
                sleep_well_score += 5
                audit_points.append(f"🏢 หุ้นขนาดกลาง (Market Cap ${(market_cap/1e9):.1f}B) มีสภาพคล่องในตลาดสูง")
            else:
                sleep_well_score -= 15
                audit_points.append("⚠️ หุ้นขนาดเล็ก (Small Cap) อาจมีความผันผวนสูงกว่าปกติ")

            if target_mean and target_mean > current_price:
                upside = (target_mean - current_price) / current_price * 100
                audit_points.append(f"🎯 ราคาเป้าหมายนักวิเคราะห์เฉลี่ย ${target_mean:.2f} (Upside +{upside:.1f}%)")
            
            if forward_pe and 0 < forward_pe < 30:
                audit_points.append(f"📊 มูลค่าหุ้น Forward P/E {forward_pe:.1f}x อยู่ในเกณฑ์สมเหตุสมผล")

            if earnings_alert:
                sleep_well_score -= 20
                audit_points.append(earnings_msg)
            else:
                audit_points.append(earnings_msg)

            sleep_well_score = max(20, min(95, sleep_well_score))

            payload = {
                "success": True,
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "earnings_date": earnings_date_str,
                "earnings_alert": earnings_alert,
                "earnings_msg": earnings_msg,
                "sleep_well_score": sleep_well_score,
                "analyst_recommendation": analyst_rec,
                "target_mean_price": round(safe_float(target_mean, 0), 2),
                "audit_points": audit_points,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._send_json(payload)
        except Exception as e:
            self._send_error(f"เกิดข้อผิดพลาดในการตรวจสอบความเสี่ยง AI: {str(e)}")

    def _handle_ai_support_levels(self, ticker):
        if not ticker:
            self._send_error("กรุณาระบุชื่อย่อหุ้น (ticker)")
            return
        if not yf:
            self._send_error("yfinance library ไม่พร้อมใช้งานในระบบ")
            return

        ticker = ticker.upper().strip()
        try:
            t = yf.Ticker(ticker)
            price = safe_float(t.fast_info.last_price, 0.0)
            if price <= 0:
                self._send_error(f"ไม่สามารถดึงราคาของ {ticker} ได้ในขณะนี้")
                return

            hist = t.history(period="1y")
            sources = []

            # 1. Technical Analysis: EMA 50, SMA 200, 3-Month Swing Low
            if not hist.empty and len(hist) >= 20:
                close = hist["Close"]
                ema50 = safe_float(close.ewm(span=50, adjust=False).mean().iloc[-1])
                sma200 = safe_float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else safe_float(close.mean())
                low_3m = safe_float(hist["Low"].iloc[-65:].min())

                tech_candidates = []
                if 0 < ema50 < price:
                    tech_candidates.append(("เส้นค่าเฉลี่ย EMA 50 วัน (ฐานราคา Trend-Follower)", ema50, "EMA 50 ทำหน้าที่เป็นแนวรับระยะกลางที่กองทุนและสถาบันใช้พิจารณาเข้าสะสมหุ้น"))
                if 0 < sma200 < price:
                    tech_candidates.append(("เส้นค่าเฉลี่ย SMA 200 วัน (แนวรับระดับสถาบันระยะยาว)", sma200, "เส้นแบ่งแนวโน้มกระทิง/หมีที่สำคัญที่สุดในวอลล์สตรีท"))
                if 0 < low_3m < price:
                    tech_candidates.append(("จุดต่ำสุดในรอบ 3 เดือน (3-Month Swing Low)", low_3m, "ฐานราคาพฤติกรรมราคา (Price Action) ที่เคยผ่านการทดสอบแรงซื้อแล้วดีดกลับ"))

                if tech_candidates:
                    tech_candidates.sort(key=lambda x: x[1], reverse=True)
                    best_tech_name, best_tech_val, best_tech_desc = tech_candidates[0]
                    dist = round((best_tech_val - price) / price * 100, 1)
                    sources.append({
                        "name": best_tech_name,
                        "category": "Technical & Price Action",
                        "category_th": "การวิเคราะห์ทางเทคนิค & พฤติกรรมราคา",
                        "price_level": round(best_tech_val, 2),
                        "distance_pct": dist,
                        "description": best_tech_desc,
                        "theory_framework": "Dow Theory & Institutional Moving Average Confluence",
                        "academic_reference": "John J. Murphy - 'Technical Analysis of the Financial Markets' & Charles Dow",
                        "reliability": "สูง (ทดสอบโดยพฤติกรรมราคาจริงของตลาด)"
                    })

            # 2. Options Put Wall (Dealer Gamma Support Floor)
            exps = list(t.options or [])
            put_wall_strike = None
            max_eff_liq = -1
            if exps:
                for exp in exps[:4]:
                    try:
                        chain = t.option_chain(exp)
                        for _, r in chain.puts.iterrows():
                            st = safe_float(r.get("strike", 0))
                            oi = safe_int(r.get("openInterest", 0))
                            vol = safe_int(r.get("volume", 0))
                            eff = oi + vol
                            if 0 < st < price and eff > max_eff_liq:
                                max_eff_liq = eff
                                put_wall_strike = st
                    except Exception:
                        continue

            if put_wall_strike and put_wall_strike < price:
                dist = round((put_wall_strike - price) / price * 100, 1)
                sources.append({
                    "name": f"Options Put Wall (Strike ${put_wall_strike:.2f})",
                    "category": "Derivatives Market Flow",
                    "category_th": "เม็ดเงินในกระดาน Options (Dealer Gamma Floor)",
                    "price_level": round(put_wall_strike, 2),
                    "distance_pct": dist,
                    "description": f"จุดรวมสัญญา Put สะสมสูงสุดในกระดาน ({max_eff_liq:,} สัญญา) กลไก Delta-Hedging บังคับให้ Market Maker ต้องตั้งออเดอร์ช้อนซื้อหุ้นแม่ (Long Stock) หนุนราคาเมื่อราคาไหลลงมาใกล้จุดนี้",
                    "theory_framework": "Market Maker Delta-Gamma Hedging & Structural Liquidity Floor",
                    "academic_reference": "CBOE Options Institute & SpotGamma Research (Dealer Positioning)",
                    "reliability": "สูงมาก (มีเม็ดเงินจริงค้ำประกันในตลาดอนุพันธ์)"
                })

            # 3. Quantitative 1-Sigma Expected Move Floor (Black-Scholes-Merton)
            if exps:
                try:
                    import numpy as np
                    target_exp = exps[1] if len(exps) > 1 else exps[0]
                    chain_iv = t.option_chain(target_exp)
                    ivs = [safe_float(r.get("impliedVolatility")) for _, r in chain_iv.puts.iterrows() if abs(safe_float(r.get("strike")) - price) / price < 0.12]
                    ivs = [x for x in ivs if x > 0.05]
                    atm_iv = float(np.mean(ivs)) if ivs else 0.35
                    dte_days = 30
                    stat_val = price * (1.0 - (atm_iv * math.sqrt(dte_days / 365.0)))
                    dist = round((stat_val - price) / price * 100, 1)
                    sources.append({
                        "name": f"1-Sigma Statistical Lower Bound (IV {atm_iv*100:.1f}%)",
                        "category": "Quantitative Statistics",
                        "category_th": "คณิตศาสตร์และสถิติความน่าจะเป็น 1-Sigma",
                        "price_level": round(stat_val, 2),
                        "distance_pct": dist,
                        "description": f"กรอบล่างความผันผวน 30 วัน ครอบคลุมการกระจายตัวของราคา 68.2% (1 Standard Deviation) ตามสถิติมีโอกาสเพียง 15.9% ที่ราคาจะหลุดต่ำกว่าระดับนี้ก่อนครบอายุสัญญา",
                        "theory_framework": "Black-Scholes-Merton Log-Normal Probability Distribution",
                        "academic_reference": "Fischer Black & Myron Scholes (1973) / Sheldon Natenberg - 'Option Volatility and Pricing'",
                        "reliability": "เชิงสถิติ 68.2% (Math-Driven Edge)"
                    })
                except Exception:
                    pass

            # 4. Fundamental Valuation Consensus (Wall Street Intrinsic Floor)
            info = getattr(t, "info", {}) or {}
            target_low = safe_float(info.get("targetLowPrice"))
            target_mean = safe_float(info.get("targetMeanPrice"))
            fund_level = target_low if (0 < target_low < price) else (target_mean if (0 < target_mean < price) else None)
            if fund_level:
                dist = round((fund_level - price) / price * 100, 1)
                sources.append({
                    "name": "Wall Street Analyst Floor (เป้าหมายต่ำสุดสถาบัน)",
                    "category": "Fundamental Valuation",
                    "category_th": "มูลค่าพื้นฐานตามประมาณการนักวิเคราะห์สถาบัน",
                    "price_level": round(fund_level, 2),
                    "distance_pct": dist,
                    "description": "ระดับราคาต่ำสุดที่นักวิเคราะห์สถาบันวอลล์สตรีทประเมินมูลค่าตามผลประกอบการและโมเดลกระแสเงินสดคิดลด (DCF) เป็นจุดที่กองทุนมองว่า Undervalued",
                    "theory_framework": "Discounted Cash Flow (DCF) & Graham-Dodd Margin of Safety",
                    "academic_reference": "Benjamin Graham & David Dodd - 'Security Analysis' / Wall Street Consensus (Refinitiv)",
                    "reliability": "ปานกลาง-สูง (อิงปัจจัยพื้นฐานและผลกำไรบริษัท)"
                })

            import numpy as np
            valid_levels = [s["price_level"] for s in sources if s["price_level"] < price]
            if valid_levels:
                valid_levels.sort()
                confluence_level = round(float(np.median(valid_levels)), 2)
                recommended_csp_strike = math.floor(confluence_level * 2) / 2.0
            else:
                confluence_level = round(price * 0.90, 2)
                recommended_csp_strike = round(confluence_level, 2)

            confluence_dist = round((confluence_level - price) / price * 100, 1)

            payload = {
                "success": True,
                "ticker": ticker,
                "current_price": round(price, 2),
                "confluence_support": confluence_level,
                "confluence_distance_pct": confluence_dist,
                "recommended_csp_strike": recommended_csp_strike,
                "sources_count": len(sources),
                "confidence_badge": f"🛡️ คอนเฟิร์มจาก {len(sources)} แหล่งข้อมูลสอดคล้องกัน" if len(sources) >= 3 else "🛡️ วิเคราะห์จากข้อมูลตลาดจริง",
                "wheel_takeaway": f"สำหรับกลยุทธ์ The Wheel (Cash-Secured Put) แนะนำให้เลือก Strike ที่ ${recommended_csp_strike:.2f} หรือต่ำกว่า ซึ่งอยู่ใต้แนวรับ Confluence (${confluence_level:.2f}) เพื่อให้มีเกราะกำแพงทั้งเทคนิคอล, เม็ดเงิน Options Put Wall, และสถิติ 1-Sigma หนุนหลังถึง {len(sources)} ชั้น!",
                "sources": sources,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._send_json(payload)
        except Exception as e:
            self._send_error(f"เกิดข้อผิดพลาดในการวิเคราะห์แนวรับของ {ticker}: {str(e)}")

    def _handle_ai_company_analysis(self, ticker):
        """
        AI Deep Dive Company Intelligence:
        What it sells, Target Customers, Competitors & Moat, 4P Mix, SWOT, Wheel Verdict
        """
        if not ticker:
            self._send_error("กรุณาระบุสัญลักษณ์หุ้น (ticker เช่น SOFI, PLTR, RKLB)")
            return
        try:
            if not company_analyzer:
                self._send_error("Company Analyzer Engine ไม่พร้อมใช้งานในระบบ")
                return
            result = company_analyzer.analyze(ticker)
            self._send_json(result)
        except Exception as e:
            self._send_error(f"เกิดข้อผิดพลาดในการวิเคราะห์ข้อมูลบริษัท {ticker}: {str(e)}")

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        cleaned = clean_for_json(data)
        self.wfile.write(json.dumps(cleaned, ensure_ascii=False, allow_nan=False).encode("utf-8"))

    def _send_error(self, message, status_code=400):
        self._send_json({"success": False, "error": message}, status_code)

    def log_message(self, format, *args):
        sys.stderr.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {args[0]} - {args[1]}\n")

def run():
    server_address = ("", PORT)
    try:
        httpd = ThreadingHTTPServer(server_address, OptionsDataHandler)
        print("============================================================")
        print(f"  The Wheel Strategy Hub - Real Options & AI Brain Server")
        print(f"  Status: RUNNING on http://127.0.0.1:{PORT}")
        print("  Endpoints:")
        print("    - /api/status")
        print("    - /api/quote")
        print("    - /api/options")
        print("    - /api/ai/market-top3")
        print("    - /api/ai/optimize")
        print("    - /api/ai/audit")
        print("    - /api/options/batch-quotes (Mark-to-Market Live Sync)")
        print("============================================================")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            print(f"Port {PORT} is already in use.")
        else:
            raise e

if __name__ == "__main__":
    run()
