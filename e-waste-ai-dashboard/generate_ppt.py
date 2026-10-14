import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette (Industrial Dark Theme)
    BG_COLOR = RGBColor(11, 15, 25)         # #0B0F19 (Deep Slate)
    CARD_BG = RGBColor(22, 30, 49)          # #161E31 (Card Background)
    CARD_BORDER = RGBColor(37, 51, 80)      # Border
    ACCENT_GREEN = RGBColor(16, 185, 129)   # #10B981 (Eco Green)
    ACCENT_CYAN = RGBColor(6, 182, 212)     # #06B6D4 (IoT Cyan)
    ACCENT_BLUE = RGBColor(59, 130, 246)    # #3B82F6 (AI Blue)
    ACCENT_AMBER = RGBColor(245, 158, 11)   # #F59E0B (Warning/Alert)
    TEXT_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC (Headings)
    TEXT_MUTED = RGBColor(148, 163, 184)    # #94A3B8 (Body)
    TEXT_WHITE = RGBColor(255, 255, 255)

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: Title, Problem & Overview
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Top Tag
    tag_card = add_card(slide1, Inches(0.8), Inches(0.6), Inches(3.2), Inches(0.4), bg_color=RGBColor(6, 40, 48), border_color=ACCENT_CYAN)
    tf_tag = tag_card.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "DNN + IoT CAPSTONE PROJECT"
    p_tag.font.bold = True
    p_tag.font.size = Pt(11)
    p_tag.font.color.rgb = ACCENT_CYAN
    p_tag.alignment = PP_ALIGN.CENTER

    # Main Title
    tx_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(1.3))
    tf = tx_box.text_frame
    tf.word_wrap = True
    p_title = tf.paragraphs[0]
    p_title.text = "EcoSort AI: Smart E-Waste Classification"
    p_title.font.bold = True
    p_title.font.size = Pt(36)
    p_title.font.color.rgb = TEXT_LIGHT

    p_sub = tf.add_paragraph()
    p_sub.text = "Automated Electronic Waste Identification, Hazard Detection & Material Recovery with MobileNetV2 & ESP32-CAM"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = ACCENT_GREEN

    # 3 Column Content on Slide 1: Problem, Solution, Highlights
    # Column 1: The Problem
    col1 = add_card(slide1, Inches(0.8), Inches(2.7), Inches(3.6), Inches(4.2))
    tf1 = col1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0.3)
    tf1.margin_right = Inches(0.3)
    tf1.margin_top = Inches(0.3)
    p = tf1.paragraphs[0]
    p.text = "⚠️ The E-Waste Challenge"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = ACCENT_AMBER

    points_prob = [
        "50M+ Metric Tons of electronic waste generated annually worldwide.",
        "Toxic Leakage: Improper landfill disposal releases Lead, Mercury, and Cadmium into soil and water tables.",
        "Manual Sorting Bottlenecks: Inefficient, hazardous to workers, and causes low recovery of precious metals (Au, Ag, Cu, Li)."
    ]
    for pt in points_prob:
        p2 = tf1.add_paragraph()
        p2.text = "• " + pt
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(10)

    # Column 2: The Solution
    col2 = add_card(slide1, Inches(4.8), Inches(2.7), Inches(3.7), Inches(4.2))
    tf2 = col2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = Inches(0.3)
    tf2.margin_right = Inches(0.3)
    tf2.margin_top = Inches(0.3)
    p = tf2.paragraphs[0]
    p.text = "💡 The EcoSort AI Solution"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = ACCENT_GREEN

    points_sol = [
        "Edge-to-Cloud Pipeline: ESP32-CAM captures physical waste items on conveyor/drop-boxes.",
        "DNN Visual Inference: MobileNetV2 TFLite classifies 10 discrete e-waste categories in <50ms.",
        "Instant Recycling Guidance: Provides automated hazard warnings, dismantling protocols, and recoverable material breakdowns."
    ]
    for pt in points_sol:
        p2 = tf2.add_paragraph()
        p2.text = "• " + pt
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(10)

    # Column 3: Key Objectives & Innovation
    col3 = add_card(slide1, Inches(8.9), Inches(2.7), Inches(3.6), Inches(4.2))
    tf3 = col3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = Inches(0.3)
    tf3.margin_right = Inches(0.3)
    tf3.margin_top = Inches(0.3)
    p = tf3.paragraphs[0]
    p.text = "🎯 Core Objectives"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = ACCENT_CYAN

    points_obj = [
        "Zero-Downtime Hot Reload: Upload and hot-swap new TFLite models on the fly without server restart.",
        "Multi-Modal Ingestion: Works via ESP32-CAM WiFi streams, PC Webcams, or manual batch image uploads.",
        "Actionable Circular Economy: Computes real-time estimated CO2 emissions prevented and recovery percentages."
    ]
    for pt in points_obj:
        p2 = tf3.add_paragraph()
        p2.text = "• " + pt
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(10)


    # ==========================================
    # SLIDE 2: Technical Architecture & Implementation
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)

    # Header
    tx_box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.1))
    tf_h2 = tx_box2.text_frame
    tf_h2.word_wrap = True
    p = tf_h2.paragraphs[0]
    p.text = "System Architecture & Engineering Workflow"
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = TEXT_LIGHT

    p_sub = tf_h2.add_paragraph()
    p_sub.text = "Seamless Integration of IoT Edge Sensing, Deep Neural Network Inference & Industrial Telemetry"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = ACCENT_CYAN

    # 3 Architectural Layers (Horizontal or 3 Vertical Cards)
    # Layer 1: IoT Edge Sensing Layer
    card_l1 = add_card(slide2, Inches(0.8), Inches(1.7), Inches(3.6), Inches(4.3))
    t1 = card_l1.text_frame
    t1.word_wrap = True
    t1.margin_left = Inches(0.3)
    t1.margin_right = Inches(0.3)
    t1.margin_top = Inches(0.3)
    p = t1.paragraphs[0]
    p.text = "1. IoT Edge Sensing Layer"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = ACCENT_CYAN

    l1_details = [
        "AI-Thinker ESP32-CAM: Low-cost edge micro-controller with OV2640 camera sensor.",
        "Wireless Streaming: Runs C++ Arduino firmware hosting an HTTP capture stream & POST client.",
        "Trigger Modes: Automated conveyor capture, hardware push button, or polling over LAN.",
        "Failover Support: Integrated fallback to local USB Webcams or direct file drag & drop."
    ]
    for d in l1_details:
        p_d = t1.add_paragraph()
        p_d.text = "• " + d
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(8)

    # Layer 2: Deep Learning & Backend Engine
    card_l2 = add_card(slide2, Inches(4.8), Inches(1.7), Inches(3.7), Inches(4.3))
    t2 = card_l2.text_frame
    t2.word_wrap = True
    t2.margin_left = Inches(0.3)
    t2.margin_right = Inches(0.3)
    t2.margin_top = Inches(0.3)
    p = t2.paragraphs[0]
    p.text = "2. AI Inference Backend"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = ACCENT_BLUE

    l2_details = [
        "MobileNetV2 Architecture: Lightweight depthwise separable convolutions optimized for edge speed.",
        "TensorFlow Lite: Quantized model (e_waste_classifier.tflite) for ultra-low latency (<50ms).",
        "FastAPI Asynchronous Server: High-throughput Python REST API endpoints for telemetry and inference.",
        "Dynamic Model Hot-Swap: In-memory tensor validation allows switching model versions without server downtime."
    ]
    for d in l2_details:
        p_d = t2.add_paragraph()
        p_d.text = "• " + d
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(8)

    # Layer 3: Presentation & Analytics Dashboard
    card_l3 = add_card(slide2, Inches(8.9), Inches(1.7), Inches(3.6), Inches(4.3))
    t3 = card_l3.text_frame
    t3.word_wrap = True
    t3.margin_left = Inches(0.3)
    t3.margin_right = Inches(0.3)
    t3.margin_top = Inches(0.3)
    p = t3.paragraphs[0]
    p.text = "3. ThingsBoard Dashboard"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = ACCENT_GREEN

    l3_details = [
        "Industrial Dark UI: Live KPI ribbon, system uptime, and multi-camera live video monitor.",
        "Knowledge Engine: 10 categorized waste items with hazard badges (Red/Yellow/Green).",
        "Real-Time Analytics: Top-3 prediction confidence distribution charts & scan history log.",
        "Role-Based Access: Secure session-based Admin portal with CSV telemetry export."
    ]
    for d in l3_details:
        p_d = t3.add_paragraph()
        p_d.text = "• " + d
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(8)

    # Bottom workflow badge
    flow_bar = add_card(slide2, Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.7), bg_color=RGBColor(16, 25, 42))
    tf_fb = flow_bar.text_frame
    tf_fb.word_wrap = True
    p_fb = tf_fb.paragraphs[0]
    p_fb.text = "Data Pipeline Flow: ESP32-CAM Sensor ➔ HTTP Ingestion ➔ TFLite Preprocessing ➔ MobileNetV2 Inference ➔ Knowledge Base Lookup ➔ Real-Time UI Dispatch"
    p_fb.font.bold = True
    p_fb.font.size = Pt(11)
    p_fb.font.color.rgb = RGBColor(186, 230, 253)
    p_fb.alignment = PP_ALIGN.CENTER


    # ==========================================
    # SLIDE 3: Results, Impact & Future Roadmap
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)

    # Header
    tx_box3 = slide3.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.1))
    tf_h3 = tx_box3.text_frame
    tf_h3.word_wrap = True
    p = tf_h3.paragraphs[0]
    p.text = "Performance Results, Environmental Impact & Roadmap"
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = TEXT_LIGHT

    p_sub = tf_h3.add_paragraph()
    p_sub.text = "Demonstrated System Efficacy, Sustainability Metrics, and Autonomous Sorting Expansion"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = ACCENT_GREEN

    # Top Row: 4 Metric Cards
    metrics = [
        ("10 Classes", "E-Waste Categories Covered", ACCENT_CYAN),
        ("< 50 ms", "Average Inference Latency", ACCENT_BLUE),
        ("90%+ Recovery", "Valuable Metal Potential (Au, Cu, Li)", ACCENT_GREEN),
        ("100% Zero-Downtime", "Dynamic Model Hot-Reloading", ACCENT_AMBER)
    ]
    card_w = Inches(2.7)
    gap = Inches(0.3)
    left_start = Inches(0.8)

    for i, (m_val, m_lbl, m_col) in enumerate(metrics):
        m_card = add_card(slide3, left_start + i * (card_w + gap), Inches(1.7), card_w, Inches(1.2))
        tf_m = m_card.text_frame
        tf_m.word_wrap = True
        tf_m.margin_top = Inches(0.18)
        p_val = tf_m.paragraphs[0]
        p_val.text = m_val
        p_val.font.bold = True
        p_val.font.size = Pt(22)
        p_val.font.color.rgb = m_col
        p_val.alignment = PP_ALIGN.CENTER

        p_lbl = tf_m.add_paragraph()
        p_lbl.text = m_lbl
        p_lbl.font.size = Pt(10)
        p_lbl.font.color.rgb = TEXT_MUTED
        p_lbl.alignment = PP_ALIGN.CENTER

    # Bottom Row: 2 Wider Cards (Environmental & Operational Impact VS Future Roadmap)
    # Card Left: Sustainability & Circular Economy
    imp_card = add_card(slide3, Inches(0.8), Inches(3.1), Inches(5.7), Inches(3.8))
    tf_imp = imp_card.text_frame
    tf_imp.word_wrap = True
    tf_imp.margin_left = Inches(0.3)
    tf_imp.margin_right = Inches(0.3)
    tf_imp.margin_top = Inches(0.3)
    p = tf_imp.paragraphs[0]
    p.text = "🌱 Environmental & Operational Impact"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = ACCENT_GREEN

    impact_points = [
        "Hazard Mitigation: Alerts technicians immediately to toxic batteries, mercury backlights, and leaded cathode tubes.",
        "Automated Circular Economy: Identifies recoverable Gold, Silver, Palladium, Copper, and Lithium for smelting facilities.",
        "Carbon Footprint Reduction: Tracks cumulative CO2 savings (kg prevented) for every unit diverted from landfills.",
        "Cost-Effective Industrial Deployment: Built on accessible hardware (<$10 ESP32-CAM) with edge intelligence."
    ]
    for pt in impact_points:
        p_i = tf_imp.add_paragraph()
        p_i.text = "• " + pt
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(8)

    # Card Right: Future Roadmap
    road_card = add_card(slide3, Inches(6.8), Inches(3.1), Inches(5.7), Inches(3.8))
    tf_road = road_card.text_frame
    tf_road.word_wrap = True
    tf_road.margin_left = Inches(0.3)
    tf_road.margin_right = Inches(0.3)
    tf_road.margin_top = Inches(0.3)
    p = tf_road.paragraphs[0]
    p.text = "🚀 Future Scope & Enhancements"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = ACCENT_CYAN

    roadmap_points = [
        "Robotic Arm Integration: Connect servo-driven pneumatic actuators for automatic mechanical bin sorting based on classification outputs.",
        "Edge TPU / NPU Acceleration: Execute on-device neural inference directly on edge silicon (e.g. Raspberry Pi AI Kit or Coral TPU).",
        "Spectral & X-Ray Analysis: Multi-spectral imaging integration to identify hidden battery chemistries and solder compositions.",
        "Decentralized Recycling Ledger: Blockchain-verified tracking of recycled rare-earth minerals for corporate ESG compliance."
    ]
    for pt in roadmap_points:
        p_r = tf_road.add_paragraph()
        p_r.text = "• " + pt
        p_r.font.size = Pt(12)
        p_r.font.color.rgb = TEXT_MUTED
        p_r.space_before = Pt(8)

    output_path = "EcoSort_AI_Presentation.pptx"
    prs.save(output_path)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    create_presentation()
