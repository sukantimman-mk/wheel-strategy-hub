# 🎡 The Wheel Strategy Hub (Options Guide & Live Trading Suite)

คู่มือการลงทุน Options ด้วยกลยุทธ์ **The Wheel Strategy** สำหรับมือใหม่ (ปูพื้นฐานตั้งแต่ 0) พร้อมระบบดึง **ราคาหุ้น & ตาราง Option Chain จริงจากตลาดสหรัฐฯ** และเครื่องมือคำนวณ-บันทึกพอร์ตใช้งานจริง

## 📁 โครงสร้างโปรเจกต์
- `index.html` — เว็บแอปพลิเคชันหลัก (Standalone HTML5 + Tailwind CSS + Vanilla JS) ดับเบิลคลิกเปิดใน Chrome, Edge, Safari ได้ทันที
- `server.py` — เซิร์ฟเวอร์ Python ดึงราคาหุ้นและ Option Chain สดๆ จากตลาดกลางสหรัฐฯ (OCC / CBOE / Nasdaq มาตรฐานเดียวกับ Webull และ IBKR)
- `start_server.bat` — ตัวเปิดเซิร์ฟเวอร์แบบดับเบิลคลิกเดียวจบ (พอร์ต 8000)

## ⚡ วิธีใช้งานระบบดึงราคา Option ตลาดจริง
1. ดับเบิลคลิกที่ไฟล์ **`start_server.bat`** (หน้าต่างดำจะขึ้นว่า `Status: RUNNING on http://127.0.0.1:8000`)
2. ดับเบิลคลิกเปิดไฟล์ **`index.html`** ในเบราว์เซอร์
3. ที่แท็บ **"2. เครื่องคำนวณ CSP & CC"** คุณจะเห็นแถบ **"⚡ ดึงข้อมูลราคา & Option Chain จริงจากตลาด"**
   - พิมพ์ชื่อหุ้นที่ต้องการ (เช่น `SOFI`, `PLTR`, `NVDA`, `AMD`, `AAPL`, `TSLA`, `SPY`) แล้วกด **"🔍 ดึงราคาตลาดจริง"**
   - เลือกดรอปดาวน์ **วันหมดอายุจริง (Expiration Date)** จากตลาด
   - ดูตาราง Option Chain จริง (Strike, Bid, Ask, Mid Premium, IV, Volume, Open Interest) พร้อมแถบสีแนะนำโซน **Delta 0.20–0.30**
   - กดปุ่ม **"🎯 เลือกลงเครื่องคำนวณ"** ระบบจะนำราคาจริงไปคำนวณผลตอบแทน จุดคุ้มทุน และวาดกราฟ Payoff Diagram ให้ทันที!

## 💡 ทำไมราคาถึงตรงกับ Webull และโบรกเกอร์อื่นๆ 100%?
ในตลาดหุ้นสหรัฐฯ สัญญา Options ทั้งหมดถูกออกและรับประกันโดย **OCC (Options Clearing Corporation)** และเผยแพร่ข้อมูลผ่าน **OPRA** ดังนั้นไม่ว่าจะดูผ่าน Webull, Interactive Brokers, Charles Schwab หรือผ่านระบบนี้ คุณจะได้ **Strike Price, วันหมดอายุ, และราคาค่าพรีเมียม Bid / Ask / Last เดียวกันเป๊ะ 100%**
