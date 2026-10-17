"""
company_analyzer.py - Fundamental Business, Economic Moat & Strategic Intelligence Engine
Analyzes:
1. What the company sells & Revenue Model (สิ่งที่บริษัทขาย / โครงสร้างรายได้)
2. Target Customers & Segments (กลุ่มลูกค้าเป้าหมาย & อำนาจผูกใจ)
3. Competitors & Economic Moat (คู่แข่งหลัก & คูเมืองการแข่งขัน 5 ด้าน)
4. 4P Marketing Mix (Product, Price, Place, Promotion)
5. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
6. Porter's 5 Forces Analysis (แรงขับเคลื่อนการแข่งขัน 5 ด้าน)
7. Financial Health & ROIC Moat (ความแข็งแกร่งทางการเงิน & ROIC vs WACC)
8. Management Quality & Insider Alignment (ธรรมาภิบาล & ผู้บริหาร)
9. The Wheel Suitability & Assignment Verdict (วิเคราะห์ความคุ้มค่าหากถูกรับมอบหุ้น)
"""

import math
from typing import Dict, Any

try:
    import yfinance as yf
except ImportError:
    yf = None

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

# =============================================================================
# CURATED KNOWLEDGE BASE FOR POPULAR WHEEL TICKERS
# =============================================================================
CURATED_PROFILES: Dict[str, Dict[str, Any]] = {
    "RKLB": {
        "what_it_sells": {
            "headline": "ผู้ให้บริการส่งดาวเทียมสู่อวกาศครบวงจร และผู้ผลิตชิ้นส่วน/ระบบดาวเทียม (Space Systems) ชั้นนำของโลก",
            "core_products": [
                "Electron Rocket: จรวดนำส่งดาวเทียมขนาดเล็กที่มีอัตราการยิงสำเร็จสูงที่สุดเป็นอันดับ 2 ของสหรัฐฯ รองจาก SpaceX",
                "Neutron Rocket: จรวดขนาดกลางรุ่นใหม่ (Reusable) สำหรับส่งกลุ่มดาวเทียมและงานความมั่นคงแห่งชาติ",
                "Space Systems (ดาวเทียม & ชิ้นส่วน): ออกแบบและสร้างยาน Photon, แผงโซลาร์เซลล์อวกาศ (SolAero), มอเตอร์ควบคุมทิศทาง, ซอฟต์แวร์ยานอวกาศ",
                "HASTE (Hypersonic Testbed): บริการทดสอบขีปนาวุธไฮเปอร์โซนิกความเร็วเหนือเสียงสำหรับกระทรวงกลาโหมสหรัฐฯ (DoD)"
            ],
            "revenue_model": "รายได้ 2 ขาหลัก: (1) Launch Services คิดค่าบริการยิงจรวดต่อเที่ยวบิน ~$7.5M - $8M, (2) Space Systems สัญญาผลิตชิ้นส่วนและดาวเทียมให้ NASA, กองทัพสหรัฐฯ และบริษัทเอกชน (สัดส่วนรายได้กว่า 65-70% มาจากส่วนนี้)"
        },
        "customers": {
            "target_segments": "ภาครัฐและความมั่นคง (B2G) + ภาคเอกชนอวกาศพาณิชย์ (B2B)",
            "key_clients": "NASA, กองทัพอวกาศสหรัฐฯ (U.S. Space Force), DARPA, Spire Global, Globalstar, Viasat, MDA",
            "customer_profile": "ลูกค้าที่ต้องการความยืดหยุ่นสูง (Dedicated Orbit) ในการส่งดาวเทียมขึ้นสู่วงโคจรเฉพาะที่จรวดขนาดใหญ่แบบ Ride-share ตอบโจทย์ไม่ได้",
            "retention_power": "สูงมาก เนื่องจากสัญญาอวกาศและงานกลาโหมมีระยะเวลาผูกพัน 3-5 ปี พร้อมทั้งมีข้อกำหนดความปลอดภัย (Security Clearance) ขั้นสูงสุดที่ผู้เล่นรายอื่นเข้ามาแทนที่ได้ยาก"
        },
        "competitors": {
            "direct_competitors": [
                "SpaceX (Falcon 9 / Transporter): ผู้นำเบอร์ 1 ของโลก (เน้นขนส่งรวมขนาดใหญ่)",
                "United Launch Alliance (ULA - Boeing/Lockheed): จรวด Vulcan (เน้นงานกลาโหมหนัก)",
                "Firefly Aerospace & Relativity Space: คู่แข่งจรวดขนาดเล็ก-กลาง",
                "Northrop Grumman & Lockheed Martin: คู่แข่งในด้าน Space Systems & Subsystems"
            ],
            "moat": "เป็นบริษัทอวกาศเชิงพาณิชย์ 'เพียงเจ้าเดียว' นอกจาก SpaceX ที่มีสถิติการยิงจรวดขึ้นวงโคจรสำเร็จเป็นประจำ (Proven Track Record 50+ ภารกิจ) และมีฐานปล่อยจรวดส่วนตัว 2 แห่ง (นิวซีแลนด์ LC-1 และสหรัฐฯ LC-2 เวอร์จิเนีย)"
        },
        "economic_moat": {
            "rating": "Narrow to Widening Moat",
            "badge": "🛡️ NARROW TO WIDENING MOAT (คูเมืองกำลังขยายตัว)",
            "trajectory": "Widening (กำลังขยายตัวต่อเนื่อง)",
            "summary": "มีคูเมืองแข็งแกร่งจากสินทรัพย์ไม่มีตัวตน (ใบอนุญาตปล่อยจรวด FAA, ฐานยิงส่วนตัว LC-1/LC-2) และต้นทุนการเปลี่ยนย้าย (Switching Costs) ในสัญญากลาโหม NASA/DoD พร้อมทั้งกำแพงเทคโนโลยีการผลิตจรวดคาร์บอนและเครื่องยนต์ 3D printing",
            "five_sources": {
                "network_effect": {"score": 3, "status": "Low", "desc": "ธุรกิจขนส่งอวกาศไม่ได้พึ่งพาผลกระทบเครือข่ายโดยตรง"},
                "switching_costs": {"score": 9, "status": "Very High", "desc": "สัญญาสร้างดาวเทียมและงานกลาโหมผูกพัน 3-5 ปี สเปกเฉพาะทางและระบบความปลอดภัยระดับทหาร ย้ายค่ายไม่ได้"},
                "cost_advantage": {"score": 8, "status": "Strong", "desc": "การผลิตเครื่องยนต์ Rutherford ด้วย 3D Printing และนำลำตัวจรวดขั้นแรกกลับมาใช้ใหม่ช่วยกดต้นทุนต่อเที่ยวบิน"},
                "intangible_assets": {"score": 9, "status": "Dominant", "desc": "สิทธิบัตรแผงโซลาร์ SolAero (ใช้บนสถานีอวกาศ/ดาวเทียมทหาร), ใบอนุญาตปล่อยจรวด FAA, และฐานปล่อยเอกชน LC-1 นิวซีแลนด์ที่ยิงได้ทุก 72 ชม."},
                "efficient_scale": {"score": 8, "status": "Strong", "desc": "ตลาด Dedicated Small Launch มีช่องว่างให้ผู้ชนะที่ประสบความสำเร็จจริงเพียง 1-2 ราย คู่แข่งสตาร์ทอัพรายอื่นทยอยล้มละลาย"}
            }
        },
        "porters_five_forces": {
            "summary": "โครงสร้างการแข่งขันได้เปรียบสูงเนื่องจากกำแพงผู้เล่นใหม่สูงลิ่ว และสินค้าทดแทนมีจำกัด",
            "buyer_power": {"level": "Medium", "level_th": "ปานกลาง", "desc": "ลูกค้าภาครัฐ (DoD/NASA) มีอำนาจต่อรองสเปกสูง แต่งบประมาณไม่อั้นและต้องการผู้ให้บริการที่ไว้ใจได้"},
            "supplier_power": {"level": "Low", "level_th": "ต่ำ (ได้เปรียบ)", "desc": "บริษัทผลิตชิ้นส่วน อุปกรณ์อิเล็กทรอนิกส์ และเครื่องยนต์เองแบบเบ็ดเสร็จ (High Vertical Integration)"},
            "threat_new_entrants": {"level": "Low", "level_th": "ต่ำมาก (กำแพงสูงมาก)", "desc": "ต้องใช้เงินทุนมหาศาล ใบอนุญาตความมั่นคง สถิติการยิงสำเร็จ และวิทยาการชั้นสูงที่ผู้เล่นใหม่เข้ามายากยิ่ง"},
            "threat_substitutes": {"level": "Low", "level_th": "ต่ำ (หาตัวแทนยาก)", "desc": "การส่งดาวเทียมสู่วงโคจรเฉพาะไม่มีทางเลือกอื่น นอกจากจรวดนำส่ง"},
            "industry_rivalry": {"level": "Medium", "level_th": "ปานกลาง", "desc": "แข่งขันกับ SpaceX ในตลาดเล็ก แต่เน้นเจาะตลาดวงโคจรเฉพาะ (Dedicated Orbit) ที่ SpaceX Rideshare ไม่ตอบโจทย์"}
        },
        "financial_moat": {
            "roic_vs_wacc": {"status": "อยู่ระหว่างช่วงลงทุน R&D (High Growth Phase)", "desc": "ธุรกิจ Space Systems เริ่มสร้างกระแสเงินสดบวก ชดเชยงบ R&D ของจรวด Neutron"},
            "free_cash_flow": {"status": "Backlog คำสั่งซื้อมูลค่า $1B+ ทยอยรับรู้", "desc": "มีสัญญาในมือค้ำประกันกระแสเงินสดในอนาคตหลายปี"},
            "balance_sheet_strength": {"status": "เงินสดและเงินลงทุนระยะสั้น $500M+", "desc": "สภาพคล่องเพียงพอรองรับการพัฒนาจรวด Neutron จนถึงเที่ยวบินแรก"},
            "altman_z_safety": "Moderate-Safe (งบดุลแข็งแกร่งกว่าสตาร์ทอัพอวกาศรายอื่นในอุตสาหกรรม)"
        },
        "management_alignment": {
            "founder_led": True,
            "leader_profile": "Peter Beck (ผู้ก่อตั้ง & CEO) - วิศวกรอวกาศระดับตำนานผู้คิดค้นเครื่องยนต์ Rutherford",
            "insider_ownership": "ประมาณ 10.5% (ผู้ก่อตั้งและผู้บริหารมี Skin in the Game สูงมาก)",
            "capital_allocation": "จัดสรรเงินทุนอย่างมีวิสัยทัศน์: เข้าซื้อกิจการ SolAero และ Virgin Orbit Assets ในราคาลดพิเศษเพื่อเสริมป้อมปราการ Space Systems"
        },
        "four_p": {
            "product": "จรวด Electron ผลิตจากคาร์บอนคอมโพสิตและเครื่องยนต์พิมพ์ 3 มิติ (Rutherford Engine), จรวด Neutron ยุคใหม่, แพลตฟอร์มดาวเทียม Photon ครบวงจร",
            "price": "Electron คิดราคา ~$7.5M - $8.5M ต่อเที่ยว (คุ้มค่าสำหรับ Dedicated Small Satellite Launch); สัญญางาน Space Systems มีมูลค่าหลักสิบล้านถึงหลายร้อยล้านดอลลาร์",
            "place": "ฐานปล่อยจรวด Launch Complex 1 (Mahia, นิวซีแลนด์) สามารถยิงได้ทุก 72 ชั่วโมง และ Launch Complex 2 (Wallops Island, เวอร์จิเนีย สหรัฐฯ)",
            "promotion": "การถ่ายทอดสดภารกิจยิงจรวดระดับโลก, การนำเสนอผลงานผ่านการประมูลสัญญาสัมปทานรัฐบาล (Federal Procurement / DoD / SDA), การสาธิตเทคโนโลยีความแม่นยำสูง"
        },
        "swot": {
            "strengths": [
                "มี Backlog คำสั่งซื้อรอรับรู้รายได้มูลค่าทะลุ $1 พันล้านดอลลาร์",
                "มีฐานะการเงินแข็งแกร่ง เงินสดในมือสูงเมื่อเทียบกับสตาร์ทอัพอวกาศรายอื่น",
                "สถิติความสำเร็จในการยิงจรวด Electron สูงเป็นอันดับ 2 ของโลกตะวันตก",
                "ธุรกิจ Space Systems สร้างกระแสเงินสดประจำอย่างสม่ำเสมอ ลดความเสี่ยงจากการเลื่อนยิงจรวด"
            ],
            "weaknesses": [
                "ยังคงมีผลขาดทุนสุทธิจากการเร่งวิจัยและพัฒนา (R&D) จรวด Neutron",
                "ต้นทุนการพัฒนาโครงสร้างพื้นฐานอวกาศสูงและใช้เวลานานก่อนคุ้มทุน",
                "Electron บรรทุกน้ำหนักได้จำกัด (300 kg) จึงต้องพึ่งพาความสำเร็จของ Neutron ในอนาคต"
            ],
            "opportunities": [
                "การเปิดตัวจรวด Neutron จะปลดล็อกตลาดกลุ่มดาวเทียมขนาดใหญ่ (Mega-Constellations) ชน SpaceX",
                "งบประมาณกลาโหมอวกาศของสหรัฐฯ (Golden Age of Space Defense) เพิ่มขึ้นต่อเนื่อง",
                "ความต้องการทดสอบอาวุธไฮเปอร์โซนิก (HASTE) เติบโตจากความตึงเครียดทางภูมิรัฐศาสตร์โลก"
            ],
            "threats": [
                "SpaceX กดดันราคาผ่านเที่ยวบินแบบหารเฉลี่ย (Ride-share Flights)",
                "ความเสี่ยงหากเที่ยวบินทดสอบ Neutron ล่าช้ากว่ากำหนดการ",
                "กฎระเบียบการบินอวกาศ (FAA licensing) และความเสี่ยงจากความล้มเหลวในการปล่อยตัว (Launch Failure)"
            ]
        },
        "wheel_verdict": {
            "score": 85,
            "badge": "HIGH CONVICTION (หุ้นอวกาศเบอร์ 2 ที่มีพื้นฐานจริง)",
            "can_hold_if_assigned": True,
            "verdict_th": "หากถูก Assign รับหุ้นที่ Strike ปลอดภัย: บริษัทมี Backlog งานรัฐบาลและเอกชนรองรับ $1B+ มีกระแสเงินสดจาก Space Systems ค้ำจุน มีโอกาสเติบโตสูงตามเมกะเทรนด์อวกาศ เหมาะสำหรับการขาย Covered Call เพื่อเก็บพรีเมียมต่อเนื่อง"
        }
    },
    "SOFI": {
        "what_it_sells": {
            "headline": "One-Stop Digital Financial Platform (Super-App ทางการเงินครบวงจร) และโครงสร้างพื้นฐาน FinTech B2B",
            "core_products": [
                "Lending Products: สินเชื่อส่วนบุคคล (Personal Loans), สินเชื่อรีไฟแนนซ์เพื่อการศึกษา (Student Loans), สินเชื่อบ้าน (Home Loans)",
                "Financial Services: บัญชีเงินฝากดอกเบี้ยสูง SoFi Money / Checking & Savings, บัตรเครดิต SoFi Credit Card, แพลตฟอร์มลงทุน SoFi Invest (หุ้น, ETF, Crypto)",
                "Technology Platform (B2B): Galileo & Technisys แพลตฟอร์มโครงสร้างพื้นฐานระบบประมวลผลธุรกรรมและ Core Banking API สำหรับ FinTech และสถาบันการเงินทั่วโลก"
            ],
            "revenue_model": "รายได้ 3 เสาหลัก: (1) ดอกเบี้ยสุทธิ (Net Interest Margin) จากการปล่อยสินเชื่อที่ต้นทุนต่ำผ่านเงินฝากสมาชิก, (2) ค่าธรรมเนียมบริการทางการเงินและการลงทุน, (3) ค่าบริการใช้ระบบเทคโนโลยี B2B (Galileo Accounts fee)"
        },
        "customers": {
            "target_segments": "กลุ่มคนรุ่นใหม่รายได้สูงแต่ยังไม่สะสมความมั่งคั่งเต็มที่ (HENRY: High Earners, Not Rich Yet) + สถาบันการเงิน B2B",
            "key_clients": "สมาชิกบุคคลทั่วไปกว่า 8.8+ ล้านคนในสหรัฐฯ และสถาบันการเงินที่เชื่อมต่อระบบ Galileo กว่า 150+ ล้านบัญชี",
            "customer_profile": "วัยทำงานอายุ 25-45 ปี ที่ชื่นชอบบริการการเงินบนสมาร์ตโฟน 100% ต้องการผลตอบแทนเงินฝากสูง และสินเชื่ออัตราดอกเบี้ยเป็นธรรม",
            "retention_power": "สูงมากจากกลยุทธ์ Financial Services Productivity Loop (FSPL) ลูกค้า 1 คนเริ่มจากฝากเงิน แล้วขยับไปใช้บัตรเครดิต กู้เงิน และลงทุนในแอปเดียว"
        },
        "competitors": {
            "direct_competitors": [
                "ธนาคารพาณิชย์ดั้งเดิม: JPMorgan Chase, Bank of America, Wells Fargo",
                "FinTech & Digital Banks: Robinhood (HOOD), Chime, Ally Financial",
                "ผู้ให้บริการสินเชื่อดิจิทัล: Upstart, Affirm, LendingClub"
            ],
            "moat": "ได้รับใบอนุญาตธนาคารเต็มรูปแบบ (National Bank Charter) ทำให้ระดมเงินฝากดอกเบี้ยต่ำได้เองโดยตรง ไม่ต้องพึ่งพิงธนาคารพันธมิตร และมีต้นทุนเงินทุน (Cost of Capital) ต่ำกว่า FinTech ทั่วไปอย่างมีนัยสำคัญ"
        },
        "economic_moat": {
            "rating": "Narrow to Widening Moat",
            "badge": "🛡️ NARROW TO WIDENING MOAT (คูเมืองธนาคารดิจิทัล)",
            "trajectory": "Widening (ขยายตัวตามยอดเงินฝากและสมาชิก)",
            "summary": "คูเมืองสำคัญคือใบอนุญาตธนาคารระดับชาติ (National Bank Charter) ที่อนุญาตให้ระดมเงินฝากประกัน FDIC ได้เอง ทำให้ต้นทุนทางการเงิน (Cost of Funds) ต่ำกว่า FinTech คู่แข่ง ผสานกับต้นทุนการเปลี่ยนย้าย (Switching Cost) ผ่าน Financial Services Productivity Loop",
            "five_sources": {
                "network_effect": {"score": 6, "status": "Moderate", "desc": "โครงสร้างพื้นฐาน Galileo ยิ่งมีสถาบันการเงินเชื่อมต่อมาก ข้อมูลการประมวลผลธุรกรรมยิ่งแม่นยำ"},
                "switching_costs": {"score": 8, "status": "High", "desc": "เมื่อลูกค้าผูกบัญชีเงินเดือน ฝากเงิน กู้สินเชื่อบ้าน และลงทุนใน SoFi การย้ายออกไปธนาคารอื่นสร้างความยุ่งยากสูง"},
                "cost_advantage": {"score": 9, "status": "Dominant", "desc": "ไม่มีต้นทุนค่าเช่าและพนักงานสาขาทางกายภาพ (Branchless) พร้อมทั้งมีเงินฝากดอกเบี้ยต่ำคอยหนุนสินเชื่อ"},
                "intangible_assets": {"score": 9, "status": "Dominant", "desc": "National Bank Charter ที่สำนักงาน OCC ควบคุมอย่างเข้มงวด ปัจจุบันยากมากที่ FinTech รายอื่นจะได้รับใบอนุญาตนี้"},
                "efficient_scale": {"score": 6, "status": "Moderate", "desc": "ตลาดการเงินในสหรัฐฯ กว้างใหญ่ แต่ตลาด Digital Native Banking มียักษ์ใหญ่ไม่กี่เจ้าที่ทำกำไรสุทธิ GAAP ได้จริง"}
            }
        },
        "porters_five_forces": {
            "summary": "ความสามารถในการแข่งขันเหนือชั้นกว่า FinTech ทั่วไปเนื่องจากมีต้นทุนเงินทุนต่ำและกำไร GAAP ยั่งยืน",
            "buyer_power": {"level": "Medium", "level_th": "ปานกลาง", "desc": "ผู้บริโภคสามารถเปรียบเทียบดอกเบี้ยเงินฝากได้ แต่ SoFi ชดเชยด้วยระบบนิเวศและสิทธิประโยชน์สมาชิก"},
            "supplier_power": {"level": "Low", "level_th": "ต่ำมาก (ได้เปรียบ)", "desc": "เงินทุนมาจากฐานเงินฝากของประชาชนโดยตรง ไม่ต้องพึ่งพาเงินกู้ดอกเบี้ยแพงจากธนาคารวอลล์สตรีท"},
            "threat_new_entrants": {"level": "Low", "level_th": "ต่ำ (มีกำแพงกฎหมาย)", "desc": "หน่วยงานกำกับดูแลของสหรัฐฯ (Fed/OCC) เข้มงวดกับการออกใบอนุญาตธนาคารใหม่แก่บริษัทเทคอย่างยิ่ง"},
            "threat_substitutes": {"level": "Medium", "level_th": "ปานกลาง", "desc": "ธนาคารดั้งเดิม (Chase, BofA) ยังคงมีฐานลูกค้าขนาดใหญ่ แต่ตามหลังด้านประสบการณ์ผู้ใช้ดิจิทัล"},
            "industry_rivalry": {"level": "High", "level_th": "สูง", "desc": "การแข่งขันในตลาดสินเชื่อและการแย่งเงินฝากในสหรัฐฯ ดุเดือด แต่ SoFi เติบโตสวนทางด้วยโมเดลแบบ All-in-One"}
        },
        "financial_moat": {
            "roic_vs_wacc": {"status": "GAAP Net Income พลิกเป็นบวกต่อเนื่อง", "desc": "กำไรสุทธิเติบโตต่อเนื่อง แสดงถึงประสิทธิภาพเงินทุนและส่วนต่างดอกเบี้ยสุทธิ (NIM) ที่แข็งแกร่ง"},
            "free_cash_flow": {"status": "กระแสเงินสดจากสินเชื่อและเงินฝากเติบโตสม่ำเสมอ", "desc": "ยอดเงินฝากเติบโตกว่า $2B+ ต่อไตรมาส"},
            "balance_sheet_strength": {"status": "อัตราส่วนเงินกองทุน (Total Capital Ratio) สูงกว่าเกณฑ์กฎหมาย", "desc": "มีเสถียรภาพรองรับความผันผวนของตลาดสินเชื่อ"},
            "altman_z_safety": "Safe Zone (ควบคุมความเสี่ยงตามเกณฑ์ธนาคารสหรัฐฯ)"
        },
        "management_alignment": {
            "founder_led": False,
            "leader_profile": "Anthony Noto (CEO) - อดีต COO Twitter, อดีต Head of Technology Investment Banking ของ Goldman Sachs, ศิษย์เก่า West Point",
            "insider_ownership": "ประมาณ 1.5% - 2.0% (CEO เข้าซื้อหุ้นบริษัทตัวเองด้วยเงินส่วนตัวในตลาดเปิดสม่ำเสมอ)",
            "capital_allocation": "มีวินัยการจัดสรรเงินทุนสูง: ซื้อ Technisys ขยาย B2B Platform และเลือกที่จะไม่แข่งขันปล่อยสินเชื่อเสี่ยงสูงในภาวะดอกเบี้ยขาขึ้น"
        },
        "four_p": {
            "product": "แอปพลิเคชันรวมศูนย์การเงินไร้รอยต่อ, ฟรีค่าธรรมเนียมแอบแฝง, ดอกเบี้ยเงินฝากสูง (APY สูงกว่าค่าเฉลี่ยธนาคารทั่วไป 8-10 เท่า), ประกันเงินฝาก FDIC สูงสุด $2M",
            "price": "สินเชื่อคิดดอกเบี้ยตามความเสี่ยง (Risk-adjusted rate), บัญชีเงินฝากฟรีค่าธรรมเนียมรายเดือน, SoFi Invest ซื้อขายหุ้น/ETF ฟรีค่าคอมมิชชัน",
            "place": "100% Digital Native ผ่าน Mobile App (iOS / Android) และเว็บไซต์ ปราศจากต้นทุนสาขาจริง",
            "promotion": "สิทธิการตั้งชื่อสนามกีฬา SoFi Stadium (สนามแข่งขัน Super Bowl และ Olympics), แคมเปญแนะนำเพื่อน (Referral Rewards), การตลาดดิจิทัลเจาะกลุ่มคนจบมหาวิทยาลัย"
        },
        "swot": {
            "strengths": [
                "มี National Bank Charter ลดต้นทุนเงินกู้และเพิ่มความน่าเชื่อถือ",
                "กำไรสุทธิตามมาตรฐาน GAAP พลิกเป็นบวกอย่างยั่งยืนต่อเนื่อง",
                "ยอดเงินฝากเติบโตสม่ำเสมอทุกไตรมาส (สัดส่วนเงินฝากคุณภาพสูง)",
                "โมเดลกระจายความเสี่ยงครบ 3 ธุรกิจ (Lending, Financial Services, Tech Platform)"
            ],
            "weaknesses": [
                "พอร์ตสินเชื่อส่วนบุคคลยังมีความอ่อนไหวต่อภาวะเศรษฐกิจถดถอยและอัตราการว่างงาน",
                "ธุรกิจ Technology Platform (Galileo) มีอัตราการเติบโตชะลอตัวลงในบางไตรมาส"
            ],
            "opportunities": [
                "การขยายผลิตภัณฑ์การลงทุน สินทรัพย์ทางเลือก และบริการบริหารความมั่งคั่ง (Wealth Management)",
                "ส่วนแบ่งการตลาดที่เพิ่มขึ้นจากการที่ผู้บริโภคย้ายเงินออกจากธนาคารสาขาดั้งเดิมสู่ดิจิทัล",
                "การเติบโตของการรีไฟแนนซ์เงินกู้นักศึกษาเมื่อมาตรการผ่อนผันของรัฐบาลสิ้นสุดลงอย่างถาวร"
            ],
            "threats": [
                "การแข่งขันด้านดอกเบี้ยเงินฝากที่รุนแรงจากธนาคารดิจิทัลคู่แข่ง",
                "ความเสี่ยงจากหนี้เสีย (Credit Losses / Charge-offs) หากเศรษฐกิจสหรัฐฯ ชะลอตัว",
                "ทิศทางอัตราดอกเบี้ยนโยบายของธนาคารกลางสหรัฐฯ (Fed Rate Cuts/Hikes)"
            ]
        },
        "wheel_verdict": {
            "score": 88,
            "badge": "SWEET SPOT WHEEL STOCK (หุ้นขวัญใจกลยุทธ์ The Wheel)",
            "can_hold_if_assigned": True,
            "verdict_th": "เหมาะกับ The Wheel เป็นอันดับต้นๆ ของตลาด: หุ้นมีสภาพคล่อง Options สูงมาก พลิกทำกำไรสุทธิ GAAP แล้ว มีใบอนุญาตธนาคารมั่นคง หากเกิด Assignment ต้นทุนต่ำกว่า $13-14 ถือรอรับการเติบโตพร้อมขาย Covered Call ได้ทุกสัปดาห์"
        }
    },
    "PLTR": {
        "what_it_sells": {
            "headline": "ผู้นำระดับโลกด้านแพลตฟอร์มปฏิบัติการข้อมูลขนาดใหญ่ (Big Data Analytics) และระบบปัญญาประดิษฐ์ระดับองค์กร (Enterprise AI)",
            "core_products": [
                "Palantir Gotham: ซอฟต์แวร์วิเคราะห์ข้อมูลเชิงลึกและวางแผนยุทธวิธีสำหรับหน่วยงานความมั่นคง กองทัพ และข่าวกรอง",
                "Palantir Foundry: ระบบปฏิบัติการข้อมูลส่วนกลางสำหรับองค์กรธุรกิจขนาดใหญ่เพื่อบริหารห่วงโซ่อุปทานและการผลิต",
                "Palantir AIP (Artificial Intelligence Platform): แพลตฟอร์มเชื่อมต่อ Large Language Models (LLM) เข้ากับฐานข้อมูลภายในองค์กรอย่างปลอดภัย",
                "Palantir Apollo: ระบบ Continuous Deployment สำหรับอัปเดตและควบคุมซอฟต์แวร์ในทุกสภาวะแวดล้อม (Cloud to Edge)"
            ],
            "revenue_model": "รายได้แบบ Subscription / Multi-Year Enterprise Contracts คิดค่าบริการตามการใช้งานและขนาดขององค์กร (แบ่งเป็น Government ~55% และ Commercial ~45%)"
        },
        "customers": {
            "target_segments": "รัฐบาลและหน่วยงานความมั่นคงระดับชาติ (Defense/Intel) + องค์กรธุรกิจชั้นนำระดับ Global 2000",
            "key_clients": "กระทรวงกลาโหมสหรัฐฯ (DoD), กองทัพบกสหรัฐฯ, CIA, NHS (สหราชอาณาจักร), BP, Airbus, Tyson Foods, Ferrari, Cleveland Clinic",
            "customer_profile": "องค์กรที่มีข้อมูลซับซ้อนมหาศาล ต้องการการตัดสินใจแบบเรียลไทม์ และต้องการระบบความปลอดภัยระดับความลับทางทหาร",
            "retention_power": "สูงที่สุดในอุตสาหกรรม (Net Retention Rate > 115%) เนื่องจากเมื่อเชื่อมต่อระบบ Palantir เข้ากับแกนหลักขององค์กรแล้ว มีต้นทุนการเปลี่ยนระบบ (Switching Cost) สูงมากจนแทบเป็นไปไม่ได้ที่จะยกเลิก"
        },
        "competitors": {
            "direct_competitors": [
                "Hyperscalers & Cloud AI: Microsoft Azure AI, Amazon AWS, Google Cloud",
                "Big Data & Analytics: Snowflake, Databricks, Splunk, C3.ai",
                "ผู้รับเหมากลาโหมด้านไอที: Booz Allen Hamilton, Leidos, Lockheed Martin"
            ],
            "moat": "ความสัมพันธ์ที่ฝังรากลึกกับกองทัพสหรัฐฯ มากว่า 20 ปี และได้รับมาตรฐานความปลอดภัยระดับสูงสุด (DoD Impact Level 6: IL6) ซึ่งคู่แข่งซอฟต์แวร์ทั่วไปแทบไม่มีทางขอผ่านได้"
        },
        "economic_moat": {
            "rating": "Wide Moat",
            "badge": "🏰 WIDE MOAT (ป้อมปราการคูเมืองกว้างขวางระดับ 20+ ปี)",
            "trajectory": "Widening (ขยายตัวรวดเร็วจากการนำ AIP ไปใช้งาน)",
            "summary": "มีคูเมืองแบบ Wide Moat แข็งแกร่งที่สุดตัวหนึ่งในกลุ่มเทคโนโลยี ขับเคลื่อนด้วยต้นทุนการเปลี่ยนย้าย (Switching Costs) ที่แทบเป็นไปไม่ได้ที่จะถอดถอน และใบอนุญาตความมั่นคงระดับสูงสุด DoD IL6 ผสานกับความลับและประสิทธิภาพของระบบ Gotham / Foundry",
            "five_sources": {
                "network_effect": {"score": 7, "status": "Moderate-High", "desc": "เมื่อพาร์ตเนอร์หรือซัพพลายเชนในอุตสาหกรรมใช้ Foundry การแลกเปลี่ยนข้อมูลระหว่างองค์กรจะยิ่งทรงพลัง"},
                "switching_costs": {"score": 10, "status": "Dominant (สูงสุด)", "desc": "เมื่อติดตั้ง Palantir เป็นระบบปฏิบัติการหลักของกองทัพหรือโรงงาน การเปลี่ยนระบบเทียบเท่ากับการผ่าตัดเปลี่ยนสมองขององค์กร"},
                "cost_advantage": {"score": 8, "status": "Strong", "desc": "Gross Margin สูงกว่า 80% และซอฟต์แวร์สร้างเสร็จแล้ว การเพิ่มลูกค้าใหม่มีต้นทุนส่วนเพิ่ม (Marginal Cost) ต่ำมาก"},
                "intangible_assets": {"score": 10, "status": "Dominant (สูงสุด)", "desc": "DoD Impact Level 6 (IL6) ความลับระดับสงคราม สิทธิบัตรสถาปัตยกรรมข้อมูล Ontology และชื่อเสียงระดับชาติ"},
                "efficient_scale": {"score": 8, "status": "Strong", "desc": "ไม่มีผู้เล่นรายใดในโลกสามารถแข่งขันกับสัญญาความมั่นคงของกระทรวงกลาโหมสหรัฐฯ ได้เท่าเทียม"}
            }
        },
        "porters_five_forces": {
            "summary": "พลังการแข่งขันอยู่ในระดับผูกขาดสำหรับงานความมั่นคง และได้เปรียบสูงในตลาดองค์กรขนาดใหญ่",
            "buyer_power": {"level": "Low", "level_th": "ต่ำ (Palantir ได้เปรียบ)", "desc": "ลูกค้าทั้งรัฐบาลและองค์กรธุรกิจไม่มีทางเลือกอื่นที่จัดการข้อมูลซับซ้อนและ AI ได้ระดับนี้"},
            "supplier_power": {"level": "Low", "level_th": "ต่ำมาก", "desc": "ซอฟต์แวร์และอัลกอริทึมพัฒนาขึ้นเองทั้งหมด ไม่ต้องพึ่งพาซัพพลายเออร์ภายนอก"},
            "threat_new_entrants": {"level": "Low", "level_th": "แทบเป็นศูนย์", "desc": "การสร้างซอฟต์แวร์ที่ผ่านการรับรองจากหน่วยข่าวกรองและกองทัพสหรัฐฯ ต้องใช้เวลากว่า 20 ปี"},
            "threat_substitutes": {"level": "Low", "level_th": "ต่ำมาก", "desc": "ไม่มีโซลูชันสำเร็จรูปใดในตลาดที่ผสาน Ontology ข้อมูลระดับ Mission-Critical ได้เทียบเท่า"},
            "industry_rivalry": {"level": "Low", "level_th": "ต่ำ", "desc": "ไม่มีคู่แข่งที่ชนกับ Gotham และ AIP ได้โดยตรงในตลาดซอฟต์แวร์ปฏิบัติการสนามรบและโรงงาน"}
        },
        "financial_moat": {
            "roic_vs_wacc": {"status": "ROIC สูงและเติบโตต่อเนื่อง", "desc": "อัตรากำไรจากการดำเนินงานเร่งตัวขึ้นอย่างรวดเร็ว (Rule of 40 คะแนนทะลุ 50-60%)"},
            "free_cash_flow": {"status": "ผลิตกระแสเงินสดอิสระระดับ $1B+ ต่อปี", "desc": "Free Cash Flow Margin สูงถึง 35-40%"},
            "balance_sheet_strength": {"status": "ปลอดหนี้ระยะยาว 100% (Zero Debt) และเงินสด $4B+", "desc": "หนึ่งในงบดุลที่ปลอดภัยที่สุดในตลาดหุ้นสหรัฐฯ"},
            "altman_z_safety": "Super Safe Zone (ความปลอดภัยทางการเงินสูงสุด ปราศจากความเสี่ยงล้มละลาย)"
        },
        "management_alignment": {
            "founder_led": True,
            "leader_profile": "Alex Karp (CEO) & Peter Thiel (Chairman/Co-founder) - ผู้นำที่มีวิสัยทัศน์ล้ำหน้าด้านภูมิรัฐศาสตร์และ AI",
            "insider_ownership": "ประมาณ 8-10% (ผู้ก่อตั้งมีอำนาจโหวตแบบ Multi-class shares ชัดเจน)",
            "capital_allocation": "เน้นลงทุนวิจัย AIP Bootcamp รุกตลาดการค้า ไม่ก่อหนี้ และเข้าซื้อหุ้นคืนเพื่อลดผลกระทบของ Stock-based compensation"
        },
        "four_p": {
            "product": "AIP แพลตฟอร์ม AI ระดับองค์กรที่เปิดทางให้ใช้งาน Generative AI บนข้อมูลความลับของบริษัทได้อย่างปลอดภัยและไม่ละเมิดลิขสิทธิ์",
            "price": "สัญญาระดับ Enterprise มูลค่าสูง ($1M - $50M+ ต่อสัญญา) ด้วยโมเดลทดลองใช้ผ่าน AIP Bootcamps แล้วขยายผล",
            "place": "ติดตั้งได้ทั้งบน Public Cloud, Private Data Center, และระบบปิดแบบไร้อินเทอร์เน็ต (Air-gapped Environments)",
            "promotion": "Palantir AIP Bootcamps (เวิร์กช็อปเชิงรุกที่ช่วยให้ลูกค้าสร้าง AI Workflow สำเร็จภายในไม่กี่วัน), การเข้าร่วมประมูลสัญญากลาโหม"
        },
        "swot": {
            "strengths": [
                "อัตรากำไรขั้นต้น (Gross Margin) สูงกว่า 80%",
                "งบดุลแข็งแกร่ง ปราศจากหนี้ระยะยาว มีเงินสดและเงินลงทุนระยะสั้นหลายพันล้านดอลลาร์",
                "เข้าคำนวณในดัชนี S&P 500 เรียบร้อยแล้ว ได้รับแรงซื้อสถาบันและกองทุน ETF สม่ำเสมอ",
                "การเติบโตของลูกค้าภาคธุรกิจ (US Commercial) เร่งตัวขึ้นอย่างรวดเร็วจากการบูมของ AIP"
            ],
            "weaknesses": [
                "ระดับมูลค่าหุ้น (Valuation P/E และ P/S) อยู่ในระดับพรีเมียมสูงมากเมื่อเทียบกับกลุ่มเทค",
                "ระยะเวลาการขาย (Sales Cycle) ในฝั่งรัฐบาลต้องใช้เวลานานและขึ้นกับงบประมาณประจำปี"
            ],
            "opportunities": [
                "การขยายตัวของงบประมาณด้าน AI อัตโนมัติทางทหาร (Project Maven / Titan)",
                "การเข้าสู่ตลาด Healthcare, Supply Chain, และการเงินพาณิชย์ทั่วโลก",
                "การต่อยอดเป็นระบบปฏิบัติการมาตรฐานของยุค Enterprise AI"
            ],
            "threats": [
                "ความเสี่ยงจากการปรับลดตัวคูณมูลค่า (Multiple Contraction) หากอัตราการเติบโตชะลอตัว",
                "แรงกดดันด้านจริยธรรมและการตรวจสอบจากองค์กรสิทธิมนุษยชนต่องานด้านการทหาร",
                "การแข่งขันจาก Big Tech (Microsoft/OpenAI) ที่พยายามรุกตลาด AI องค์กร"
            ]
        },
        "wheel_verdict": {
            "score": 92,
            "badge": "ENTERPRISE AI MONSTER (หุ้นพื้นฐานเกรด A+ ป้อมปราการไร้คู่แข่ง)",
            "can_hold_if_assigned": True,
            "verdict_th": "เหมาะกับการทำ The Wheel อย่างยิ่ง: พรีเมียมของ Options สูงมากเนื่องจากความผันผวนสูง หากถูก Assignment ที่ราคา OTM ก็การันตีได้ถือหุ้นผู้นำ Big Data/AI อันดับ 1 ของโลกที่ไม่มีหนี้และงบดุลแกร่ง สามารถขาย Covered Call รับค่าเช่าแพงๆ ได้ยาวนาน"
        }
    },
    "NVDA": {
        "what_it_sells": {
            "headline": "มหาอำนาจชิปประมวลผลกราฟิกและ AI Accelerator ควบรวมแพลตฟอร์มซอฟต์แวร์ประมวลผลเต็มรูปแบบ (Full-Stack AI Platform)",
            "core_products": [
                "Data Center AI GPUs: สถาปัตยกรรม Hopper (H100, H200) และสถาปัตยกรรมยุคใหม่ Blackwell (B200, GB200)",
                "Networking: อุปกรณ์เชื่อมต่อความเร็วสูง Quantum InfiniBand และ Spectrum-X Ethernet",
                "Software & Ecosystem: CUDA Programming Platform, NVIDIA AI Enterprise, Omniverse (Digital Twin)",
                "Gaming & Auto: ชิปการ์ดจอ GeForce RTX สำหรับคอมพิวเตอร์ และแพลตฟอร์มชิปรถยนต์ขับขี่อัตโนมัติ DRIVE"
            ],
            "revenue_model": "รายได้กว่า 85-90% มาจาก Data Center คิดค่าลิขสิทธิ์ฮาร์ดแวร์เซิร์ฟเวอร์ AI และซอฟต์แวร์สิทธิบัตร CUDA แบบผูกขาด"
        },
        "customers": {
            "target_segments": "Cloud Service Providers (Hyperscalers), บริษัทปัญญาประดิษฐ์ระดับโลก, รัฐบาล (Sovereign AI), บริษัทรถยนต์",
            "key_clients": "Microsoft, Meta, Google, Amazon AWS, Oracle, OpenAI, xAI (Elon Musk), Tesla",
            "customer_profile": "ยักษ์ใหญ่เทคโนโลยีที่จำเป็นต้องสร้างโครงสร้างพื้นฐาน AI ขนาดยักษ์เพื่อฝึกฝนและประมวลผลโมเดลภาษาขนาดใหญ่ (LLMs)",
            "retention_power": "เกือบ 100% เพราะวิศวกรซอฟต์แวร์ AI ทั่วโลกเขียนโค้ดและพัฒนาบนแพลตฟอร์ม CUDA มากว่า 15 ปี ไม่สามารถย้ายไปค่ายอื่นได้ง่าย"
        },
        "competitors": {
            "direct_competitors": [
                "ชิปประมวลผลคู่แข่ง: AMD (MI300X/MI325), Intel (Gaudi 3)",
                "Custom In-house ASICs: Google TPU, Amazon Trainium/Inferentia, Meta MTIA, Microsoft Maia"
            ],
            "moat": "ระบบนิเวศซอฟต์แวร์ CUDA ที่เป็นกำแพงเหล็ก (Software Moat) ผสานกับนวัตกรรมการออกแบบชิปที่ก้าวล้ำหน้าคู่แข่งในตลาดอย่างน้อย 1-2 ปีเต็ม"
        },
        "economic_moat": {
            "rating": "Wide Moat",
            "badge": "🏰 WIDE MOAT (ราชาแห่งคูเมืองผูกขาดตลาด AI โลก)",
            "trajectory": "Widening (ขยายตัวต่อเนื่องด้วย Blackwell และ Full-stack Rack Solutions)",
            "summary": "คูเมืองของ NVIDIA ไร้เทียมทานจาก 3 ด้านหลัก: (1) Network Effect ของ CUDA Ecosystem นักพัฒนา 4+ ล้านคน, (2) Switching Costs สูงลิ่วในการพอร์ตโมเดล AI, และ (3) Cost Advantage จากการเป็นผู้ซื้อกำลังการผลิต 3nm/4nm อันดับหนึ่งของ TSMC",
            "five_sources": {
                "network_effect": {"score": 10, "status": "Dominant (สูงสุด)", "desc": "CUDA เป็นมาตรฐานอุตสาหกรรม ยิ่งนักวิจัยใช้ CUDA เขียนเปเปอร์มากเท่าไร ชิป NVIDIA ก็ยิ่งเป็นตัวเลือกแรกของโลก"},
                "switching_costs": {"score": 10, "status": "Dominant (สูงสุด)", "desc": "การพอร์ตโค้ด AI ขนาดยักษ์จาก CUDA ไปรันบนสถาปัตยกรรมอื่น (เช่น ROCm ของ AMD) ต้องใช้เวลา วิศวกร และความเสี่ยงบั๊กมหาศาล"},
                "cost_advantage": {"score": 9, "status": "Strong", "desc": "สั่งผลิตชิปและ CoWoS Packaging จาก TSMC ในปริมาณมหาศาลที่สุด ทำให้ได้ต้นทุนต่อทรานซิสเตอร์ต่ำกว่าคู่แข่ง"},
                "intangible_assets": {"score": 10, "status": "Dominant (สูงสุด)", "desc": "สิทธิบัตร GPU Tensor Core, สถาปัตยกรรม Blackwell, NVLink Switch, และแบรนด์ที่เป็นสัญลักษณ์ของ AI"},
                "efficient_scale": {"score": 9, "status": "Dominant", "desc": "คู่แข่งต้องทุ่มเงิน R&D หลายหมื่นล้านดอลลาร์เพื่อสร้างชิป แต่ NVIDIA มีงบ R&D ปีละหลายพันล้านดอลลาร์ทิ้งห่างไปอีกก้าวเสมอ"}
            }
        },
        "porters_five_forces": {
            "summary": "มีอำนาจการตั้งราคา (Pricing Power) และการครองตลาดสูงสุดแห่งยุคเซมิคอนดักเตอร์",
            "buyer_power": {"level": "Low", "level_th": "ต่ำมาก (NVIDIA กำหนดราคาได้)", "desc": "แม้ลูกค้าคือยักษ์ใหญ่ Big Tech (Microsoft/Meta) แต่ทุกคนแย่งชิงโควตาชิป ไม่กล้าต่อรองราคา"},
            "supplier_power": {"level": "Medium", "level_th": "ปานกลาง", "desc": "พึ่งพา TSMC ในการผลิต แต่ NVIDIA เป็นลูกค้ารายใหญ่ที่สุดรายหนึ่งและมีอำนาจจองไลน์ผลิตล่วงหน้า"},
            "threat_new_entrants": {"level": "Low", "level_th": "แทบเป็นศูนย์", "desc": "การออกแบบชิป AI ระดับ 2 แสนล้านทรานซิสเตอร์และระบบระบายความร้อนด้วยของเหลวต้องใช้ R&D มหาศาล"},
            "threat_substitutes": {"level": "Low", "level_th": "ต่ำ", "desc": "ชิป ASIC เฉพาะทางประหยัดไฟในงานอนุมาน (Inference) แต่ไม่สามารถแทนที่ความยืดหยุ่นของ GPU ในการเทรนโมเดล"},
            "industry_rivalry": {"level": "Low", "level_th": "ต่ำมาก (ส่วนแบ่งตลาด 80-90%)", "desc": "AMD MI300X ชิงส่วนแบ่งได้บางส่วน แต่ NVIDIA ทิ้งห่างด้วย Blackwell และ NVLink Networking"}
        },
        "financial_moat": {
            "roic_vs_wacc": {"status": "ROIC สูงเกิน 60-70% (สูงสุดในประวัติศาสตร์ทุนนิยม)", "desc": "สร้างผลตอบแทนต่อเงินลงทุนสูงกว่าต้นทุนเงินทุนมหาศาล สร้าง Economic Profit มหาศาล"},
            "free_cash_flow": {"status": "Free Cash Flow ทะลุ $50B+ ต่อปี", "desc": "ผลิตเงินสดเร็วกว่าที่บริษัทจะนำไปลงทุนได้ทัน"},
            "balance_sheet_strength": {"status": "เงินสดสุทธิมหาศาล (Net Cash Position)", "desc": "ไม่มีปัญหาหนี้สิน สามารถซื้อหุ้นคืนและลงทุน R&D ได้ไม่อั้น"},
            "altman_z_safety": "Super Safe Zone (งบดุลแข็งแกร่งระดับ AAA เสมือนธนาคารกลางแห่ง AI)"
        },
        "management_alignment": {
            "founder_led": True,
            "leader_profile": "Jensen Huang (ผู้ก่อตั้ง & CEO) - วิสัยทัศน์ที่นำหน้าอุตสาหกรรม 10 ปี ทุ่มเทเงินลงทุนใน CUDA ตั้งแต่ปี 2006",
            "insider_ownership": "ประมาณ 3.5% (มูลค่าหุ้นที่ Jensen ถือครองสูงกว่า $100B+ มีส่วนได้เสียเต็มร้อย)",
            "capital_allocation": "จัดสรรเงินทุนระดับอัจฉริยะ: ซื้อ Mellanox (สร้างระบบ InfiniBand Networking) ซึ่งกลายเป็นป้อมปราการ AI ที่คู่แข่งตามไม่ทัน"
        },
        "four_p": {
            "product": "ชิป GPU Blackwell และ Superchip ที่รวม CPU+GPU+ระบบระบายความร้อนด้วยของเหลวในเซิร์ฟเวอร์เดียว",
            "price": "การตั้งราคาแบบผูกขาดอำนาจตลาด (Pricing Power สูงสุด) ชิป 1 ตัวมีราคาสูงถึง $30,000 - $40,000 และอัตรากำไรขั้นต้นกว่า 75%",
            "place": "จำหน่ายผ่านพันธมิตรผู้ผลิตเซิร์ฟเวอร์ (Supermicro, Dell, HP, Foxconn) และผู้ให้บริการคลาวด์ทั่วโลก",
            "promotion": "งานประชุมเทคโนโลยีระดับโลก NVIDIA GTC (ปาฐกถาโดย Jensen Huang), การร่วมมือเชิงกลยุทธ์กับรัฐบาลและสถาบันวิจัย"
        },
        "swot": {
            "strengths": [
                "ส่วนแบ่งการตลาดในชิป AI Data Center สูงกว่า 80-90%",
                "กระแสเงินสดอิสระ (Free Cash Flow) มหาศาลหลายหมื่นล้านดอลลาร์ต่อปี",
                "CUDA Ecosystem เป็นกำแพงป้องกันคู่แข่งที่แข็งแกร่งที่สุดในโลกไอที",
                "ผู้นำ Jensen Huang มีวิสัยทัศน์ที่นำหน้าคู่แข่งเสมอ"
            ],
            "weaknesses": [
                "พึ่งพาโรงงานผลิตชิปภายนอก TSMC (ไต้หวัน) แทบจะ 100%",
                "การกระจุกตัวของลูกค้ารายใหญ่ (Big Tech 4-5 เจ้ามีสัดส่วนรายได้กว่า 40%)"
            ],
            "opportunities": [
                "เมกะเทรนด์ Sovereign AI (ทุกประเทศต้องการมีโครงสร้างพื้นฐาน AI ประจำชาติ)",
                "การนำ AI ไปประยุกต์ใช้ในหุ่นยนต์มนุษย์ (Humanoid Robots) และรถยนต์ไร้คนขับ",
                "การอัปเกรดเซิร์ฟเวอร์ทั่วโลกเข้าสู่สถาปัตยกรรม Blackwell"
            ],
            "threats": [
                "มาตรการจำกัดการส่งออกชิปขั้นสูงไปยังประเทศจีนของรัฐบาลสหรัฐฯ",
                "ความเสี่ยงทางภูมิรัฐศาสตร์บริเวณช่องแคบไต้หวันกระทบโรงงาน TSMC",
                "ลูกค้า Big Tech กำลังเร่งพัฒนาชิปของตนเองเพื่อลดการพึ่งพา NVIDIA"
            ]
        },
        "wheel_verdict": {
            "score": 95,
            "badge": "TITAN OF AI (ราชาแห่งยุค AI ที่พื้นฐานแกร่งที่สุด)",
            "can_hold_if_assigned": True,
            "verdict_th": "หุ้นคุณภาพสูงสุดสำหรับการทำ The Wheel: มีความผันผวนและค่าพรีเมียมสูงมาก ทำให้สร้างกระแสเงินสดรายสัปดาห์ได้อย่างคุ้มค่า หากถูก Assign ที่ราคา OTM ก็ได้เป็นเจ้าของหุ้นโครงสร้างพื้นฐานของโลกยุคใหม่ที่ไม่มีวันล้มละลาย"
        }
    }
}

# Generic Sector Heuristics fallback
SECTOR_DEFAULTS = {
    "Technology": {
        "what_it_sells_template": "ผลิตภัณฑ์ซอฟต์แวร์ ฮาร์ดแวร์คอมพิวเตอร์ และบริการดิจิทัลคลาวด์",
        "customers_template": "องค์กรธุรกิจทุกขนาด (B2B Enterprise) และผู้บริโภคยุคดิจิทัล (B2C)",
        "competitors_template": "บริษัทเทคโนโลยีในกลุ่มอุตสาหกรรมเดียวกันในตลาดหลักทรัพย์สหรัฐฯ",
        "four_p": {
            "product": "นวัตกรรมซอฟต์แวร์และฮาร์ดแวร์ประสิทธิภาพสูง อัปเดตผ่านระบบคลาวด์",
            "price": "การตั้งราคาตามความคุ้มค่าและโมเดลสมัครสมาชิก (Subscription / License)",
            "place": "แพลตฟอร์มดิจิทัลออนไลน์ และช่องทางตัวแทนจำหน่ายระดับโลก",
            "promotion": "การตลาดดิจิทัล การจัดงานสัมมนาเทคโนโลยี และการสร้างแบรนด์นวัตกรรม"
        },
        "swot": {
            "strengths": ["ทรัพย์สินทางปัญญาและสิทธิบัตรเทคโนโลยี", "ความสามารถในการขยายขนาดธุรกิจอย่างรวดเร็ว (High Scalability)", "อัตรากำไรขั้นต้นอยู่ในเกณฑ์สูง"],
            "weaknesses": ["ค่าใช้จ่ายด้านการวิจัยและพัฒนา (R&D) สูง", "ต้องปรับตัวตามวงจรเทคโนโลยีใหม่อย่างรวดเร็ว"],
            "opportunities": ["การนำ AI และระบบอัตโนมัติเข้ามาเพิ่มประสิทธิภาพ", "การขยายตลาดสู่ระดับสากล"],
            "threats": ["การแข่งขันที่รุนแรงจากคู่แข่งเทครายใหญ่", "ความเสี่ยงด้านความปลอดภัยทางไซเบอร์และกฎหมายคุ้มครองข้อมูล"]
        }
    },
    "Industrials": {
        "what_it_sells_template": "เครื่องจักรกล โครงสร้างพื้นฐานอุตสาหกรรม การบิน อวกาศ และการป้องกันประเทศ",
        "customers_template": "หน่วยงานรัฐบาล กองทัพ ภาคอุตสาหกรรมหนัก และบริษัทขนส่งโลจิสติกส์",
        "competitors_template": "ผู้ผลิตและผู้รับเหมาอุตสาหกรรมหนักรายใหญ่ในสหรัฐฯ และต่างประเทศ",
        "four_p": {
            "product": "เครื่องจักรกลและยุทโธปกรณ์มาตรฐานสูง ทนทาน ปลอดภัยตามมาตรฐานสากล",
            "price": "การประมูลสัญญาโครงการระยะยาว (Contract Bidding) และบริการบำรุงรักษา",
            "place": "เครือข่ายโรงงานผลิตและศูนย์ซ่อมบำรุงในจุดยุทธศาสตร์",
            "promotion": "การประมูลโครงการภาครัฐ การร่วมงานแสดงนวัตกรรมอุตสาหกรรมระดับโลก"
        },
        "swot": {
            "strengths": ["สัญญาจ้างระยะยาวและมี Backlog รองรับ", "กำแพงการเข้าสู่อุตสาหกรรมสูง (High Barriers to Entry)"],
            "weaknesses": ["ต้องลงทุนในสินทรัพย์ถาวร (Capital Intensive) สูง", "ระยะเวลาส่งมอบงานขึ้นกับห่วงโซ่อุปทาน"],
            "opportunities": ["งบประมาณการลงทุนโครงสร้างพื้นฐานและความมั่นคงที่เพิ่มขึ้น", "การเปลี่ยนผ่านสู่เทคโนโลยีอุตสาหกรรมสีเขียว"],
            "threats": ["ราคาวัตถุดิบและความผันผวนของต้นทุนพลังงาน", "ข้อพิพาททางภูมิรัฐศาสตร์และข้อจำกัดการส่งออก"]
        }
    },
    "Financial Services": {
        "what_it_sells_template": "บริการทางการเงิน การปล่อยสินเชื่อ บัญชีเงินฝาก การลงทุน และประกันภัย",
        "customers_template": "บุคคลทั่วไป ธุรกิจขนาดย่อม และบริษัทขนาดใหญ่ที่ต้องการบริหารเงินทุน",
        "competitors_template": "ธนาคารพาณิชย์ สถาบันการเงิน และสตาร์ทอัพฟินเทค (FinTech)",
        "four_p": {
            "product": "ผลิตภัณฑ์การเงินครบวงจร สินเชื่อ เงินฝาก บัตรเครดิต และระบบจัดการความมั่งคั่ง",
            "price": "อัตราดอกเบี้ยและค่าธรรมเนียมธุรกรรมที่แข่งขันได้ในตลาด",
            "place": "แอปพลิเคชันดิจิทัล โมบายแบงก์กิ้ง และสาขาบริการ",
            "promotion": "แคมเปญสิทธิประโยชน์ ดอกเบี้ยพิเศษ และการสร้างความน่าเชื่อถือของแบรนด์"
        },
        "swot": {
            "strengths": ["ฐานเงินฝากและลูกค้ามีความเหนียวแน่น", "มีกระแสเงินสดจากส่วนต่างดอกเบี้ย (NIM) สม่ำเสมอ"],
            "weaknesses": ["ต้นทุนการปฏิบัติตามกฎระเบียบของหน่วยงานกำกับดูแล (Compliance)", "ความเสี่ยงจากหนี้เสียในภาวะเศรษฐกิจซบเซา"],
            "opportunities": ["การต่อยอดสู่บริการดิจิทัลแบงก์กิ้งเต็มรูปแบบ", "การบริหารสินทรัพย์และการลงทุนที่เติบโตตามความมั่งคั่ง"],
            "threats": ["ความผันผวนของอัตราดอกเบี้ยนโยบาย", "การแข่งขันแย่งชิงเงินฝากจากธนาคารดิจิทัล"]
        }
    }
}

class CompanyAnalyzer:
    def __init__(self):
        self.cache = {}

    def analyze(self, ticker: str) -> Dict[str, Any]:
        ticker = (ticker or "SOFI").upper().strip()

        if ticker in self.cache:
            return self.cache[ticker]

        # 1. Fetch Live Yahoo Finance Profile
        company_info = {}
        if yf:
            try:
                t = yf.Ticker(ticker)
                company_info = getattr(t, "info", {}) or {}
            except Exception:
                pass

        long_name = company_info.get("longName") or company_info.get("shortName") or ticker
        sector = company_info.get("sector") or "Technology"
        industry = company_info.get("industry") or "General Industry"
        market_cap = safe_float(company_info.get("marketCap"), 0.0)
        summary = company_info.get("longBusinessSummary") or ""
        website = company_info.get("website") or ""
        country = company_info.get("country") or "United States"
        employees = company_info.get("fullTimeEmployees") or 0

        # Financial metrics for moat estimation
        gross_margins = safe_float(company_info.get("grossMargins"), 0.40)
        operating_margins = safe_float(company_info.get("operatingMargins"), 0.15)
        return_on_equity = safe_float(company_info.get("returnOnEquity"), 0.12)
        debt_to_equity = safe_float(company_info.get("debtToEquity"), 50.0)
        current_ratio = safe_float(company_info.get("currentRatio"), 1.5)
        insider_pct = safe_float(company_info.get("heldPercentInsiders"), 0.03) * 100
        inst_pct = safe_float(company_info.get("heldPercentInstitutions"), 0.60) * 100
        overall_risk = company_info.get("overallRisk") or 5

        # Check Curated Profile First
        if ticker in CURATED_PROFILES:
            profile = CURATED_PROFILES[ticker]
            result = {
                "success": True,
                "ticker": ticker,
                "company_name": long_name,
                "sector": sector,
                "industry": industry,
                "market_cap": market_cap,
                "market_cap_formatted": f"${(market_cap/1e9):.2f}B" if market_cap >= 1e9 else f"${(market_cap/1e6):.2f}M",
                "country": country,
                "employees": f"{employees:,}" if employees else "N/A",
                "website": website,
                "what_it_sells": profile["what_it_sells"],
                "customers": profile["customers"],
                "competitors": profile["competitors"],
                "economic_moat": profile["economic_moat"],
                "porters_five_forces": profile["porters_five_forces"],
                "financial_moat": profile["financial_moat"],
                "management_alignment": profile["management_alignment"],
                "four_p": profile["four_p"],
                "swot": profile["swot"],
                "wheel_verdict": profile["wheel_verdict"]
            }
            self.cache[ticker] = result
            return result

        # Dynamic Synthesizer for Any Other Ticker
        sec_template = SECTOR_DEFAULTS.get(sector, SECTOR_DEFAULTS["Technology"])
        
        summary_snippet = summary[:280] + "..." if len(summary) > 280 else summary
        headline = f"ผู้นำในกลุ่ม {industry} ให้บริการ{sec_template['what_it_sells_template']}"

        # Synthesize Moat Rating based on Market Cap and Gross Margins
        is_wide = market_cap >= 50e9 and gross_margins >= 0.50
        is_narrow = market_cap >= 5e9 or gross_margins >= 0.35

        moat_rating = "Wide Moat" if is_wide else ("Narrow Moat" if is_narrow else "No Moat")
        moat_badge = "🏰 WIDE MOAT (ป้อมปราการกว้างขวางระดับ 20+ ปี)" if is_wide else ("🛡️ NARROW MOAT (มีป้อมปราการระดับ 10 ปี)" if is_narrow else "⚖️ NO MOAT (แข่งขันด้านราคาสูง)")

        dyn_moat = {
            "rating": moat_rating,
            "badge": moat_badge,
            "trajectory": "Stable (คูเมืองมั่นคง)" if market_cap >= 10e9 else "Monitor Trajectory",
            "summary": f"หุ้น {ticker} มีความได้เปรียบเชิงแข่งขันในกลุ่ม {industry} โดยมี Gross Margin อยู่ที่ {gross_margins*100:.1f}% และมีฐานลูกค้าในภาคส่วน {sector} ช่วยสร้างเกราะป้องกันคู่แข่ง",
            "five_sources": {
                "network_effect": {"score": 7 if sector == "Technology" else 4, "status": "Moderate" if sector == "Technology" else "Low", "desc": "ขึ้นอยู่กับความหนาแน่นของผู้ใช้งานและแพลตฟอร์มในระบบ"},
                "switching_costs": {"score": 8 if gross_margins > 0.45 else 5, "status": "Strong" if gross_margins > 0.45 else "Moderate", "desc": "ลูกค้าองค์กรมีต้นทุนการเปลี่ยนผู้ให้บริการ โดยเฉพาะสัญญาระยะยาว"},
                "cost_advantage": {"score": 8 if market_cap > 20e9 else 6, "status": "Scale Advantage", "desc": f"ขนาดมูลค่าตลาด ${(market_cap/1e9):.1f}B ช่วยสร้างการประหยัดต่อขนาด (Economies of Scale)"},
                "intangible_assets": {"score": 8 if sector in ["Technology", "Healthcare"] else 6, "status": "Patents & Brands", "desc": "สิทธิบัตร นวัตกรรม และความน่าเชื่อถือของตราสินค้าในอุตสาหกรรม"},
                "efficient_scale": {"score": 7 if sector == "Industrials" else 5, "status": "Market Dependent", "desc": "ขนาดตลาดที่รองรับผู้เล่นรายใหญ่ได้อย่างมีเสถียรภาพ"}
            }
        }

        dyn_porters = {
            "summary": f"แรงกดดันการแข่งขันในอุตสาหกรรม {industry} อยู่ในระดับที่บริหารจัดการได้สำหรับบริษัทขนาดใหญ่",
            "buyer_power": {"level": "Medium", "level_th": "ปานกลาง", "desc": "ผู้ซื้อมีทางเลือกในตลาด แต่ขึ้นอยู่กับความคุ้มค่าและความจำเพาะของผลิตภัณฑ์"},
            "supplier_power": {"level": "Medium", "level_th": "ปานกลาง", "desc": "ขึ้นอยู่กับความสามารถในการจัดหาวัตถุดิบและคู่ค้าห่วงโซ่อุปทาน"},
            "threat_new_entrants": {"level": "Low" if market_cap > 10e9 else "Medium", "level_th": "ต่ำ (มีกำแพงเงินทุน)" if market_cap > 10e9 else "ปานกลาง", "desc": f"การเข้าสู่ตลาดต้องใช้เงินลงทุนและมาตรฐานอุตสาหกรรม {industry}"},
            "threat_substitutes": {"level": "Medium", "level_th": "ปานกลาง", "desc": "สินค้าทดแทนขึ้นกับนวัตกรรมใหม่และการเปลี่ยนแปลงทางเทคโนโลยี"},
            "industry_rivalry": {"level": "Medium", "level_th": "ปานกลางถึงสูง", "desc": "แข่งขันกับบริษัทชั้นนำในกลุ่มเดียวกันของดัชนี S&P 500 / Russell 1000"}
        }

        dyn_financial = {
            "roic_vs_wacc": {"status": "ผลตอบแทนเงินทุนเป็นบวก" if return_on_equity > 0.08 else "อยู่ในเกณฑ์ปกติ", "desc": f"ROE อยู่ที่ {return_on_equity*100:.1f}% และ Operating Margin อยู่ที่ {operating_margins*100:.1f}%"},
            "free_cash_flow": {"status": "มีกระแสเงินสดจากการดำเนินงาน", "desc": "สร้างกระแสเงินสดหมุนเวียนเพื่อลงทุนต่อยอดธุรกิจ"},
            "balance_sheet_strength": {"status": f"หนี้สินต่อทุน D/E อยู่ที่ {debt_to_equity:.1f}%", "desc": f"Current Ratio {current_ratio:.2f} เท่า มีสภาพคล่องหมุนเวียนระยะสั้นเพียงพอ"},
            "altman_z_safety": "Safe Zone (ปลอดภัย)" if debt_to_equity < 150 else "Watchlist (ควรติดตามภาระหนี้)"
        }

        dyn_management = {
            "founder_led": False,
            "leader_profile": f"ทีมผู้บริหารมืออาชีพในกลุ่มอุตสาหกรรม {industry}",
            "insider_ownership": f"{insider_pct:.1f}% (ถือครองโดยผู้บริหาร)",
            "institutional_ownership": f"{inst_pct:.1f}% (กองทุนสถาบันถือหุ้น)",
            "capital_allocation": "จัดสรรเงินทุนเพื่อขยายส่วนแบ่งตลาด วิจัยและพัฒนา และเสริมความแข็งแกร่งของงบดุล"
        }

        result = {
            "success": True,
            "ticker": ticker,
            "company_name": long_name,
            "sector": sector,
            "industry": industry,
            "market_cap": market_cap,
            "market_cap_formatted": f"${(market_cap/1e9):.2f}B" if market_cap >= 1e9 else f"${(market_cap/1e6):.2f}M",
            "country": country,
            "employees": f"{employees:,}" if employees else "N/A",
            "website": website,
            "what_it_sells": {
                "headline": headline,
                "summary_raw": summary_snippet,
                "core_products": [
                    f"ผลิตภัณฑ์และโซลูชันหลักในกลุ่ม {industry}",
                    "บริการสนับสนุนทางเทคนิคและสัญญาระยะยาวสำหรับลูกค้าองค์กร",
                    "การวิจัยและพัฒนานวัตกรรมเพื่อเพิ่มมูลค่าทางธุรกิจ"
                ],
                "revenue_model": f"รายได้จากการจำหน่ายผลิตภัณฑ์ ค่าธรรมเนียมบริการ และสัญญาจัดจำหน่ายในอุตสาหกรรม {sector}"
            },
            "customers": {
                "target_segments": sec_template["customers_template"],
                "key_clients": f"กลุ่มลูกค้าสถาบัน องค์กรชั้นนำ และผู้บริโภคในภาคส่วน {industry}",
                "customer_profile": "ลูกค้าที่มองหาประสิทธิภาพ ความน่าเชื่อถือ และมาตรฐานคุณภาพระดับอุตสาหกรรม",
                "retention_power": "อยู่ในระดับปานกลางถึงสูง โดยขึ้นอยู่กับความคุ้มค่าและต้นทุนในการสลับผู้ให้บริการ (Switching Cost)"
            },
            "competitors": {
                "direct_competitors": [
                    f"บริษัทชั้นนำในกลุ่ม {industry} ของดัชนี S&P 500 / Russell 1000",
                    "ผู้เล่นระดับโลกที่มีขนาดและผลิตภัณฑ์ใกล้เคียงกัน"
                ],
                "moat": f"ความเชี่ยวชาญเฉพาะทางในอุตสาหกรรม {industry}, ฐานลูกค้าเดิมที่มั่นคง, และการประหยัดจากขนาด"
            },
            "economic_moat": dyn_moat,
            "porters_five_forces": dyn_porters,
            "financial_moat": dyn_financial,
            "management_alignment": dyn_management,
            "four_p": sec_template["four_p"],
            "swot": sec_template["swot"],
            "wheel_verdict": {
                "score": 85 if is_wide else (75 if is_narrow else 65),
                "badge": "STABLE WHEEL CANDIDATE" if market_cap >= 10e9 else "MONITOR CAREFULLY",
                "can_hold_if_assigned": market_cap >= 5e9,
                "verdict_th": f"หุ้น {ticker} มีมูลค่าตลาด ${(market_cap/1e9):.1f}B อยู่ในกลุ่ม {industry} หากต้องการใช้กลยุทธ์ The Wheel ควรเลือกระดับ Strike ที่ต่ำกว่าราคาตลาดอย่างน้อย 10-15% (Deep OTM) เพื่อสร้าง Margin of Safety ในกรณีเกิดการรับมอบหุ้นจริง"
            }
        }
        self.cache[ticker] = result
        return result

company_analyzer = CompanyAnalyzer()
