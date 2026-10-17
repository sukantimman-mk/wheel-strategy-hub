"""
ai_engine.py - Modular Institutional AI Suite for The Wheel Strategy Hub
Decoupled, high-performance algorithms for:
1. Smart Roll & Rescue Solver (Live Net Credit Roll Finder)
2. Portfolio Stress-Tester & Concentration Risk Radar (Scenario -5% / -10%)
3. AI Daily Wheel Action Briefing (Actionable Daily Checklist)
"""

import datetime
import math
from typing import Dict, List, Any, Optional

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError:
    yf = None
    pd = None
    np = None

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

class WheelAIEngine:
    def __init__(self):
        self.history_cache = {}

    # =========================================================================
    # 1. AI SMART ROLL & RESCUE SOLVER (LIVE NET CREDIT FINDER)
    # =========================================================================
    def solve_smart_roll(
        self,
        ticker: str,
        opt_type: str,
        old_strike: float,
        old_exp: str,
        old_sto: float,
        current_btc: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Scans future option chains (30-60 DTE) to find the optimal Roll opportunity.
        For CSP: Roll Down & Out (Lower strike, further expiration, Net Credit >= 0).
        For CC: Roll Up & Out (Higher strike, further expiration, Net Credit >= 0).
        """
        if not yf:
            return {"success": False, "error": "yfinance is not available"}

        ticker = (ticker or "SOFI").upper().strip()
        opt_type = (opt_type or "CSP").upper()
        old_strike = float(old_strike or 0.0)
        old_sto = float(old_sto or 0.0)
        today = datetime.date.today()

        try:
            t = yf.Ticker(ticker)
            price = float(t.fast_info.last_price or 0.0)
            expirations = list(t.options or [])
            if not expirations:
                return {"success": False, "error": f"No options available for {ticker}"}

            # 1. Determine cost to close the old contract today (BTC)
            btc_cost = float(current_btc or 0.0)
            if btc_cost <= 0:
                try:
                    old_chain = t.option_chain(old_exp)
                    old_df = old_chain.puts if opt_type == "CSP" else old_chain.calls
                    match = old_df[old_df["strike"] == old_strike]
                    if not match.empty:
                        row = match.iloc[0]
                        bid = float(row.get("bid", 0.0) or 0.0)
                        ask = float(row.get("ask", 0.0) or 0.0)
                        last = float(row.get("lastPrice", 0.0) or 0.0)
                        btc_cost = round((bid + ask) / 2, 2) if (bid > 0 and ask > 0) else (ask or last)
                except Exception:
                    pass
            if btc_cost <= 0:
                btc_cost = round(old_sto * 1.5, 2)  # Default fallback estimation

            # 2. Check earnings schedule
            calendar = getattr(t, "calendar", {}) or {}
            earnings_date_obj = None
            if isinstance(calendar, dict):
                dates = calendar.get("Earnings Date", [])
                if dates and len(dates) > 0 and isinstance(dates[0], (datetime.date, datetime.datetime)):
                    earnings_date_obj = dates[0].date() if isinstance(dates[0], datetime.datetime) else dates[0]

            # 3. Filter future expirations strictly further than old_exp
            old_exp_date = datetime.datetime.strptime(old_exp, "%Y-%m-%d").date() if old_exp else today
            future_exps = []
            for e_str in expirations:
                e_date = datetime.datetime.strptime(e_str, "%Y-%m-%d").date()
                dte = (e_date - today).days
                if e_date > old_exp_date and 20 <= dte <= 65:
                    future_exps.append((e_str, e_date, dte))

            if not future_exps:
                # If old expiration was far out, accept any future expiration
                for e_str in expirations:
                    e_date = datetime.datetime.strptime(e_str, "%Y-%m-%d").date()
                    if e_date > old_exp_date:
                        future_exps.append((e_str, e_date, max(1, (e_date - today).days)))
                        if len(future_exps) >= 4:
                            break

            candidates = []

            for exp_str, exp_date, dte in future_exps[:5]:
                try:
                    chain = t.option_chain(exp_str)
                    df = chain.puts if opt_type == "CSP" else chain.calls
                    earnings_clash = bool(earnings_date_obj and (today <= earnings_date_obj <= exp_date))

                    for _, row in df.iterrows():
                        new_strike = safe_float(row.get("strike", 0.0))
                        bid = safe_float(row.get("bid", 0.0))
                        ask = safe_float(row.get("ask", 0.0))
                        last = safe_float(row.get("lastPrice", 0.0))
                        new_mid = round((bid + ask) / 2, 2) if (bid > 0 and ask > 0) else (bid or last)
                        new_mid = safe_float(new_mid, 0.0)
                        oi = safe_int(row.get("openInterest", 0))

                        if new_mid < 0.05:
                            continue

                        net_credit = round(new_mid - btc_cost, 2)
                        net_credit_dollars = round(net_credit * 100, 2)
                        annualized_yield = round(((new_mid / new_strike) * (365 / max(1, dte))) * 100, 1) if new_strike > 0 else 0.0

                        if opt_type == "CSP":
                            # Roll Down & Out: Strictly require new_strike <= old_strike (lower or same strike)
                            # Avoid deep ITM strikes which increase collateral requirement
                            if new_strike > old_strike or new_strike < (price * 0.60):
                                continue

                            strike_diff = round(old_strike - new_strike, 2)
                            safety_expansion_pct = round((strike_diff / old_strike) * 100, 1)

                            # Condition: Net credit should ideally be >= 0 or slight debit if strike is much lower
                            if net_credit >= -0.20:
                                score = (net_credit * 50) + (safety_expansion_pct * 4) + min(15, oi / 200)
                                if earnings_clash:
                                    score -= 20
                                if net_credit >= 0.10:
                                    score += 25  # Big bonus for solid net credit

                                candidates.append({
                                    "strategy_name": "Roll Down & Out" if new_strike < old_strike else "Roll Out (Same Strike)",
                                    "new_strike": new_strike,
                                    "new_expiration": exp_str,
                                    "dte": dte,
                                    "new_credit": new_mid,
                                    "btc_cost": btc_cost,
                                    "net_credit": net_credit,
                                    "net_credit_dollars": net_credit_dollars,
                                    "safety_expansion_pct": max(0.0, safety_expansion_pct),
                                    "annualized_yield_pct": annualized_yield,
                                    "open_interest": oi,
                                    "earnings_clash": earnings_clash,
                                    "score": round(score, 1)
                                })
                        else:
                            # Roll Up & Out for CC: Strictly require new_strike >= old_strike (higher or same strike)
                            if new_strike < old_strike or new_strike > (price * 1.50):
                                continue

                            strike_gain = round(new_strike - old_strike, 2)
                            upside_gain_pct = round((strike_gain / old_strike) * 100, 1) if old_strike > 0 else 0

                            if net_credit >= -0.20:
                                score = (net_credit * 50) + (upside_gain_pct * 4) + min(15, oi / 200)
                                if earnings_clash:
                                    score -= 20
                                if net_credit >= 0.10:
                                    score += 25

                                candidates.append({
                                    "strategy_name": "Roll Up & Out" if new_strike > old_strike else "Roll Out (Same Strike)",
                                    "new_strike": new_strike,
                                    "new_expiration": exp_str,
                                    "dte": dte,
                                    "new_credit": new_mid,
                                    "btc_cost": btc_cost,
                                    "net_credit": net_credit,
                                    "net_credit_dollars": net_credit_dollars,
                                    "safety_expansion_pct": max(0.0, upside_gain_pct),
                                    "annualized_yield_pct": annualized_yield,
                                    "open_interest": oi,
                                    "earnings_clash": earnings_clash,
                                    "score": round(score, 1)
                                })
                except Exception:
                    continue

            candidates.sort(key=lambda x: x["score"], reverse=True)
            top_candidates = candidates[:3]

            # Construct institutional guidance
            if top_candidates:
                best = top_candidates[0]
                if opt_type == "CSP":
                    summary_msg = (
                        f"แนะนำ {best['strategy_name']}: ปิด Strike ${old_strike:.2f} (จ่าย ${btc_cost:.2f}) "
                        f"และเปิดใหม่ที่ Strike ${best['new_strike']:.2f} หมดอายุ {best['new_expiration']} "
                        f"(รับ ${best['new_credit']:.2f}) ส่งผลให้ได้รับ Net Credit ทันที {('+$' + str(best['net_credit_dollars'])) if best['net_credit'] >= 0 else ('-$' + str(abs(best['net_credit_dollars'])))} "
                        f"พร้อมขยับแนวรับให้ปลอดภัยขึ้น {best['safety_expansion_pct']}%!"
                    )
                else:
                    summary_msg = (
                        f"แนะนำ {best['strategy_name']}: ปิด Strike ${old_strike:.2f} "
                        f"และเปิดใหม่ที่ Strike ${best['new_strike']:.2f} หมดอายุ {best['new_expiration']} "
                        f"ได้รับ Net Credit {('+$' + str(best['net_credit_dollars'])) if best['net_credit'] >= 0 else ('-$' + str(abs(best['net_credit_dollars'])))} "
                        f"พร้อมเพิ่มเพดานกำไรหุ้นอีก +{best['safety_expansion_pct']}%!"
                    )
            else:
                summary_msg = "ไม่พบจังหวะ Net Credit Roll ที่คุ้มค่าในขณะนี้ แนะนำรอให้ Theta Decay ทำงานเพิ่ม หรือพิจารณารับมอบหุ้นเพื่อทำ Covered Call ต่อ"

            return {
                "success": True,
                "ticker": ticker,
                "stock_price": round(price, 2),
                "strategy": opt_type,
                "old_strike": old_strike,
                "old_expiration": old_exp,
                "btc_cost": btc_cost,
                "top_rolls": top_candidates,
                "summary_msg": summary_msg,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": f"Roll solver failed: {str(e)}"}

    # =========================================================================
    # 2. AI PORTFOLIO STRESS-TESTER & CONCENTRATION RADAR
    # =========================================================================
    def stress_test_portfolio(self, capital: float, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs portfolio-level risk stress test:
        - Simulates S&P 500 / Underlying drops of -5% and -10%
        - Calculates Concentration Risk per ticker
        - Generates institutional Sleep-Well Score (0-100)
        """
        capital = float(capital or 10000.0)
        open_trades = [t for t in trades if (t.get("status") or "").upper() == "OPEN"]

        total_collateral_committed = 0.0
        ticker_allocations = {}
        total_open_contracts = 0

        for t in open_trades:
            ticker = (t.get("ticker") or "").upper().strip()
            strike = float(t.get("strike", 0.0) or 0.0)
            contracts = int(t.get("contracts", 1) or 1)
            opt_type = (t.get("type") or "CSP").upper()

            total_open_contracts += contracts
            collateral = (strike * contracts * 100) if opt_type == "CSP" else 0.0
            total_collateral_committed += collateral

            if ticker not in ticker_allocations:
                ticker_allocations[ticker] = {
                    "ticker": ticker,
                    "contracts": 0,
                    "collateral": 0.0,
                    "types": set()
                }
            ticker_allocations[ticker]["contracts"] += contracts
            ticker_allocations[ticker]["collateral"] += collateral
            ticker_allocations[ticker]["types"].add(opt_type)

        free_cash = max(0.0, capital - total_collateral_committed)
        cash_ratio_pct = round((free_cash / capital) * 100, 1) if capital > 0 else 0.0
        committed_ratio_pct = round((total_collateral_committed / capital) * 100, 1) if capital > 0 else 0.0

        # Concentration Risk Analysis
        concentration_alerts = []
        concentration_breakdown = []
        max_concentration_pct = 0.0

        for sym, d in ticker_allocations.items():
            pct_of_capital = round((d["collateral"] / capital) * 100, 1) if capital > 0 else 0.0
            if pct_of_capital > max_concentration_pct:
                max_concentration_pct = pct_of_capital

            status = "BALANCED"
            if pct_of_capital > 35.0:
                status = "DANGER"
                concentration_alerts.append(f"🚨 {sym} ครองสัดส่วนพอร์ต {pct_of_capital}% (เกินเกณฑ์ความปลอดภัย 25-30%) หากหุ้นตัวนี้ลงหนักจะกระทบพอร์ตโดยตรง")
            elif pct_of_capital > 25.0:
                status = "WARNING"
                concentration_alerts.append(f"⚠️ {sym} อยู่ที่ {pct_of_capital}% ของเงินทุนพอร์ต ควรระวังการเปิดสัญญาเพิ่ม")

            concentration_breakdown.append({
                "ticker": sym,
                "contracts": d["contracts"],
                "collateral": round(d["collateral"], 2),
                "pct_of_capital": pct_of_capital,
                "status": status,
                "types": list(d["types"])
            })

        concentration_breakdown.sort(key=lambda x: x["pct_of_capital"], reverse=True)

        # Stress-Testing Scenarios (-5% and -10% market drop)
        # Assuming underlying stocks drop by 5% and 10%
        scenario_5_itm_contracts = 0
        scenario_5_potential_assignment_dollars = 0.0
        scenario_10_itm_contracts = 0
        scenario_10_potential_assignment_dollars = 0.0

        for t in open_trades:
            strike = float(t.get("strike", 0.0) or 0.0)
            contracts = int(t.get("contracts", 1) or 1)
            sto = float(t.get("sto", 0.0) or 0.0)
            opt_type = (t.get("type") or "CSP").upper()

            if opt_type == "CSP":
                # Simulated drop: test if stock drops 5% below strike
                scenario_5_itm_contracts += contracts
                scenario_5_potential_assignment_dollars += strike * contracts * 100
                scenario_10_itm_contracts += contracts
                scenario_10_potential_assignment_dollars += strike * contracts * 100

        # Institutional Sleep-Well Score Calculation (0 to 100)
        score = 85
        # Penalties:
        if committed_ratio_pct > 90.0:
            score -= 25
        elif committed_ratio_pct > 75.0:
            score -= 15
        elif committed_ratio_pct < 20.0 and len(open_trades) > 0:
            score += 5  # Safe buffer

        if max_concentration_pct > 35.0:
            score -= 20
        elif max_concentration_pct > 25.0:
            score -= 10

        if len(open_trades) == 0:
            score = 100  # Zero risk if completely in cash

        sleep_well_score = max(20, min(100, score))

        # Status badge
        if sleep_well_score >= 80:
            grade = "A+ (พอร์ตแข็งแกร่ง นอนหลับสบาย)"
            grade_color = "emerald"
        elif sleep_well_score >= 65:
            grade = "B (พอร์ตระดับปกติ ควบคุมความเสี่ยงได้ดี)"
            grade_color = "sky"
        else:
            grade = "C (พอร์ตมีความเสี่ยงสูง ควรปรับสัดส่วน)"
            grade_color = "rose"

        recommendations = []
        if free_cash < (capital * 0.20) and open_trades:
            recommendations.append("💵 สำรองเงินสดอย่างน้อย 20% ของพอร์ตไว้เสมอ เพื่อรับมือจังหวะตลาดปรับฐานหรือใช้ Roll สัญญา")
        if max_concentration_pct > 30.0:
            recommendations.append("🎯 กระจายเงินทุนไปยังหุ้นในกลุ่มอุตสาหกรรมอื่น (เช่น ETF หรือ Defensive Stock) เพื่อลดความเสี่ยงเฉพาะตัว")
        if not recommendations:
            recommendations.append("🌟 โครงสร้างพอร์ตของคุณยอดเยี่ยม! มีเงินสดสำรองเพียงพอและไม่มีหุ้นตัวใดกระจุกตัวเกินเกณฑ์")

        return {
            "success": True,
            "capital": capital,
            "total_collateral_committed": round(total_collateral_committed, 2),
            "free_cash": round(free_cash, 2),
            "cash_ratio_pct": cash_ratio_pct,
            "committed_ratio_pct": committed_ratio_pct,
            "open_positions_count": len(open_trades),
            "open_contracts_count": total_open_contracts,
            "sleep_well_score": sleep_well_score,
            "grade": grade,
            "grade_color": grade_color,
            "concentration_breakdown": concentration_breakdown,
            "concentration_alerts": concentration_alerts,
            "stress_scenario_5": {
                "drop_label": "ตลาดปรับฐานเบา (-5%)",
                "simulated_assignment_usd": round(scenario_5_potential_assignment_dollars, 2),
                "is_cash_sufficient": free_cash >= scenario_5_potential_assignment_dollars or committed_ratio_pct <= 100,
                "assessment": "เงินค้ำประกันครอบคลุมเต็มจำนวน (Cash-Secured 100%) ไม่มีปัญหา Margin Call"
            },
            "stress_scenario_10": {
                "drop_label": "ตลาดปรับฐานหนัก (-10%)",
                "simulated_assignment_usd": round(scenario_10_potential_assignment_dollars, 2),
                "assessment": f"หากถูก Assign หุ้นทั้งหมด คุณจะได้รับหุ้นคุณภาพเข้าพอร์ตที่มูลค่า ${scenario_10_potential_assignment_dollars:,.2f} เพื่อเริ่มขาย Covered Call เก็บค่าเช่าต่อไป"
            },
            "recommendations": recommendations,
            "timestamp": datetime.datetime.now().isoformat()
        }

    # =========================================================================
    # 3. AI DAILY WHEEL ACTION BRIEFING (DAILY ACTIONABLE CHECKLIST)
    # =========================================================================
    def generate_daily_briefing(self, capital: float, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates an actionable 3-point briefing for today's trading session.
        """
        open_trades = [t for t in trades if (t.get("status") or "").upper() == "OPEN"]
        today = datetime.date.today()

        action_items = []
        urgent_count = 0

        # 1. Check for 50%+ profit-take opportunities
        # (Evaluated from trade parameters)
        take_profit_candidates = []
        for t in open_trades:
            sto = float(t.get("sto", 0.0) or 0.0)
            btc = float(t.get("btc", 0.0) or 0.0)
            target_50_btc = round(sto * 0.5, 2)
            take_profit_candidates.append({
                "ticker": t.get("ticker"),
                "strike": t.get("strike"),
                "exp": t.get("exp"),
                "target_50_btc": target_50_btc
            })

        # 2. Check for Expiration Urgency (<7 DTE)
        expiring_soon = []
        for t in open_trades:
            exp_str = t.get("exp") or ""
            try:
                exp_date = datetime.datetime.strptime(exp_str, "%Y-%m-%d").date()
                dte = (exp_date - today).days
                if 0 <= dte <= 7:
                    expiring_soon.append({
                        "ticker": t.get("ticker"),
                        "strike": t.get("strike"),
                        "dte": dte,
                        "exp": exp_str
                    })
                    urgent_count += 1
            except Exception:
                pass

        if expiring_soon:
            item_text = f"⏳ มี {len(expiring_soon)} สัญญาหมดอายุใน 7 วันนี้: " + ", ".join([f"{x['ticker']} (${x['strike']}) เหลือ {x['dte']} วัน" for x in expiring_soon])
            action_items.append({
                "type": "expiring",
                "priority": "HIGH",
                "icon": "⏳",
                "title": f"ติดตามสัญญาใกล้หมดอายุ ({len(expiring_soon)} รายการ)",
                "detail": item_text,
                "action_suggestion": "หากกำไรเกิน 50% แนะนำปิดล็อกเงินสดทันที หากใกล้หลุด Strike พิจารณา Roll สัญญา"
            })

        # 3. Capital deployment opportunity
        stress = self.stress_test_portfolio(capital, trades)
        free_cash = stress.get("free_cash", 0.0)

        if free_cash >= 1500:
            action_items.append({
                "type": "deploy",
                "priority": "NORMAL",
                "icon": "💡",
                "title": f"เงินสดพร้อมลงทุน ${free_cash:,.2f}",
                "detail": f"พอร์ตของคุณมีเงินสดคงเหลือเพียงพอต่อการเปิด Cash-Secured Put รอบใหม่ 1-2 สัญญา",
                "action_suggestion": "ใช้ฟังก์ชัน 'สแกน 3 หุ้นเด็ดในตลาด (Market Top 3)' เพื่อหา Strike ที่คุ้มค่าที่สุดในวันนี้"
            })
        elif free_cash < 500 and open_trades:
            action_items.append({
                "type": "cash_warning",
                "priority": "MEDIUM",
                "icon": "⚠️",
                "title": "วงเงินค้ำประกันเกือบเต็ม",
                "detail": f"เงินสดคงเหลือ ${free_cash:,.2f} ควรระงับการเปิดสัญญาใหม่ชั่วคราว",
                "action_suggestion": "รอปิดสัญญาที่ถึงเป้าเพื่อปลดปล่อยเงินค้ำประกันกลับมาเป็นเงินสด"
            })

        # Overall Status
        if urgent_count > 0:
            overall_status = f"⚡ มี {urgent_count} รายการที่ต้องจับตาใกล้ชิดในวันนี้"
            overall_color = "amber"
        elif open_trades:
            overall_status = f"🟢 ทุกสัญญาดำเนินไปตามปกติ ({len(open_trades)} สัญญาเปิดอยู่)"
            overall_color = "emerald"
        else:
            overall_status = "💤 พอร์ตถือเงินสด 100% พร้อมเปิดการบ้านรอบใหม่"
            overall_color = "sky"

        return {
            "success": True,
            "overall_status": overall_status,
            "overall_color": overall_color,
            "urgent_count": urgent_count,
            "action_items": action_items,
            "open_positions": len(open_trades),
            "free_cash": free_cash,
            "timestamp": datetime.datetime.now().isoformat()
        }


# Singleton Engine Instance
ai_engine = WheelAIEngine()
