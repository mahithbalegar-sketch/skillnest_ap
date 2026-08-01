import io
import streamlit as st
from google import genai  # Modern unified Google GenAI SDK

# Initialize the official Google GenAI client securely using Streamlit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    # Fallback initialization if secrets are missing locally
    client = genai.Client()

# ReportLab modules for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    TableStyle,
)

# Page Configuration
st.set_page_config(
    page_title="Skill Nest - AP Syllabus Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling & Gorgeous UI Enhancements
st.markdown(
    """
    <style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .stButton>button {
        background: linear-gradient(90deg, #2b6cb0 0%, #3182ce 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .header-card {
        background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .ai-response-card {
        background: white;
        border-left: 5px solid #3182ce;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 15px;
        margin-bottom: 25px;
        color: #2d3748;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "email" not in st.session_state:
    st.session_state.email = ""
if "plan" not in st.session_state:
    st.session_state.plan = None
if "grade" not in st.session_state:
    st.session_state.grade = "Grade 10"
if "board" not in st.session_state:
    st.session_state.board = "AP State Board"
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# ---------------------------------------------------------
# DETAILED AP STATE SYLLABUS DATABASE (Grades 5 to 12)
# ---------------------------------------------------------
AP_SYLLABUS_DATABASE = {
    "Grade 5": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Numbers & Large Scale Operations",
            "detailed_notes": """<b>1. INDIAN & INTERNATIONAL PLACE VALUE SYSTEMS:</b> Comprehensive study of periods, places, and reading/writing numbers up to 9 digits. Extensive analysis of place value vs face value with practical fiscal examples.<br/><br/>
            <b>2. FUNDAMENTAL ARITHMETIC OPERATIONS:</b> Detailed procedures for multi-digit addition, subtraction, multiplication, and long division with remainders.<br/><br/>
            <b>3. ESTIMATION AND APPROXIMATION:</b> Rules and rounding techniques to the nearest tens, hundreds, thousands, ten-thousands, and millions.<br/><br/>
            <b>4. FACTORS AND MULTIPLES:</b> Prime and composite numbers, divisibility tests for 2, 3, 5, 10, common factors, HCF, and LCM."""
        }
    ],
    "Grade 6": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Knowing Numbers & Fractions",
            "detailed_notes": """<b>1. NUMBER LINE EXTENSION:</b> Positive and negative numbers representation and magnitude comparisons.<br/><br/>
            <b>2. FRACTIONS & DECIMALS:</b> Proper, improper, mixed fractions, addition, and subtraction with unlike denominators."""
        }
    ],
    "Grade 7": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Integers & Rational Numbers",
            "detailed_notes": """<b>1. PROPERTIES OF INTEGERS:</b> Closure, commutative, associative, and distributive laws under arithmetic operations.<br/><br/>
            <b>2. RATIONAL NUMBERS:</b> Standard forms, positive/negative rational numbers on number lines."""
        }
    ],
    "Grade 8": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Rational Numbers & Linear Equations",
            "detailed_notes": """<b>1. DENSE PROPERTY:</b> Finding infinite rational numbers between two rational numbers.<br/><br/>
            <b>2. LINEAR EQUATIONS:</b> Constructing and solving algebraic equations with variables on both sides."""
        }
    ],
    "Grade 9": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Real Numbers & Polynomials",
            "detailed_notes": """<b>1. REAL NUMBER SYSTEM:</b> Rational vs irrational numbers and geometrical representation.<br/><br/>
            <b>2. POLYNOMIALS:</b> Degree, coefficients, zeroes, Remainder Theorem, and Factor Theorem."""
        }
    ],
    "Grade 10": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Real Numbers & Number Theory",
            "detailed_notes": """<b>1. EUCLID'S DIVISION LEMMA & ALGORITHM:</b> Detailed mathematical statement $a = bq + r$ ($0 \\le r < b$). Iterative application for calculating HCF of large integers.<br/><br/>
            <b>2. FUNDAMENTAL THEOREM OF ARITHMETIC:</b> Prime factorization uniqueness theorem and HCF/LCM relations."""
        },
        {
            "subject": "Physical Science",
            "chapter": "Chapter 1: Chemical Reactions & Optics",
            "detailed_notes": """<b>1. CHEMICAL EQUATIONS:</b> Conservation of mass law and systematic balancing techniques.<br/><br/>
            <b>2. LIGHT REFLECTION & REFRACTION:</b> Spherical mirrors, mirror formula, magnification, and Snell's law."""
        }
    ],
    "Grade 11 (Inter 1st Year)": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Functions, Matrices & Trigonometry",
            "detailed_notes": """<b>1. FUNCTIONS THEORY:</b> Domain, co-range, injective, surjective, and bijective mappings.<br/><br/>
            <b>2. MATRICES:</b> Matrix addition, scalar multiplication, determinants, and inverse via adjoint matrix."""
        }
    ],
    "Grade 12 (Inter 2nd Year)": [
        {
            "subject": "Mathematics",
            "chapter": "Chapter 1: Advanced Calculus & Probability",
            "detailed_notes": """<b>1. INTEGRAL CALCULUS:</b> Indefinite integrals, integration by substitution, and partial fractions.<br/><br/>
            <b>2. PROBABILITY:</b> Conditional probability, multiplication theorem, and Bayes' theorem."""
        }
    ]
}


# ---------------------------------------------------------
# MULTI-PAGE PDF GENERATOR
# ---------------------------------------------------------
def generate_large_pdf(grade, board, plan_type, chapters_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=16, leading=20,
                                 textColor=colors.HexColor("#1A365D"), alignment=1)
    sub_title_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontSize=9,
                                     textColor=colors.HexColor("#718096"), alignment=1)
    ch_header_style = ParagraphStyle("ChHeader", parent=styles["Heading2"], fontSize=13, leading=15,
                                     textColor=colors.HexColor("#1A365D"))
    body_style = ParagraphStyle("BodyCustom", parent=styles["BodyText"], fontSize=9, leading=13.5,
                                textColor=colors.HexColor("#2D3748"))

    story.append(Paragraph("<b>SKILL NEST — OFFICIAL ACADEMIC HANDBOOK</b>", title_style))
    story.append(
        Paragraph(f"Curriculum: {board} | Standard: {grade} | Tier: {plan_type} | Student Edition", sub_title_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2B6CB0"), spaceBefore=5, spaceAfter=15))

    for idx, ch in enumerate(chapters_data):
        story.append(Paragraph(f"<b>[{ch['subject'].upper()}]</b> {ch['chapter']}", ch_header_style))
        story.append(Spacer(1, 6))

        full_text = ch['detailed_notes']
        paragraphs_list = [Paragraph(p.strip(), body_style) for p in full_text.split("<br/><br/>") if p.strip()]
        table_data = [[p] for p in paragraphs_list]

        notes_table = LongTable(table_data, colWidths=[550])
        notes_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 8)
        ]))
        story.append(notes_table)
        story.append(Spacer(1, 15))

        if idx < len(chapters_data) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------
# PAGE 1: LOGIN / REGISTER PAGE
# ---------------------------------------------------------
if st.session_state.current_page == "login":
    st.markdown("""
        <div class="header-card">
            <h1>🎓 Skill Nest Portal</h1>
            <p>AP State Syllabus Learning Companion (Grades 5 to 12) — 100% Free & Secure Access</p>
        </div>
    """, unsafe_allow_html=True)

    col1 = st.columns(1)[0]
    with col1:
        st.subheader("Student Details")
        username = st.text_input("Full Name")
        email = st.text_input("School Email Address")

        grade_options = list(AP_SYLLABUS_DATABASE.keys())
        selected_grade = st.selectbox("Select Class / Grade", grade_options)
        selected_board = st.selectbox("Select Curriculum Board", ["AP State Board"])

        if st.button("Proceed to Plans ➔"):
            if username and email:
                st.session_state.user = username
                st.session_state.email = email
                st.session_state.grade = selected_grade
                st.session_state.board = selected_board
                st.session_state.current_page = "plans"
                st.rerun()
            else:
                st.error("Please enter both your name and email address.")


# ---------------------------------------------------------
# PAGE 2: PLANS SELECTION PAGE
# ---------------------------------------------------------
elif st.session_state.current_page == "plans":
    st.markdown("""
        <div class="header-card">
            <h1>Choose Your Learning Plan</h1>
            <p>Select the plan that fits your academic goals</p>
        </div>
    """, unsafe_allow_html=True)

    col_free, col_prem = st.columns(2)

    with col_free:
        with st.container(border=True):
            st.markdown("### 🆓 Free Plan")
            st.markdown("**PDF Study Materials Only**")
            st.divider()
            st.markdown("❌ No AI Study Partner")
            st.markdown("✔️ Access to Grade PDF Handbooks")
            st.write("")
            if st.button("Select Free Plan", key="btn_free"):
                st.session_state.plan = "Free"
                st.session_state.current_page = "dashboard"
                st.rerun()

    with col_prem:
        with st.container(border=True):
            st.markdown("### 💎 Premium Plan (₹50)")
            st.markdown("**Complete Comprehensive Package**")
            st.divider()
            st.markdown("✔️ Complete PDF Handbooks")
            st.markdown("✔️ **Study with AI** Custom Assistant (Powered by Gemini API)")
            if st.button("Select Premium Plan", key="btn_prem"):
                st.session_state.plan = "Premium"
                st.session_state.current_page = "payment"
                st.rerun()

    st.divider()
    if st.button("⬅ Back to Login"):
        st.session_state.current_page = "login"
        st.rerun()


# ---------------------------------------------------------
# PAGE 3: PAYMENT PAGE (PREMIUM ONLY)
# ---------------------------------------------------------
elif st.session_state.current_page == "payment":
    st.markdown("""
        <div class="header-card">
            <h1>💳 Premium Plan Payment</h1>
            <p>Complete your registration to unlock full curriculum features</p>
        </div>
    """, unsafe_allow_html=True)

    st.write(f"**Student Name:** {st.session_state.user}")
    st.write(f"**Email:** {st.session_state.email}")
    st.write(f"**Class:** {st.session_state.grade} ({st.session_state.board})")
    st.write(f"**Amount to Pay:** ₹50")

    st.divider()
    st.subheader("Payment Option")
    st.radio("Payment Selection:", ("Send cash/details to school administration",))

    if st.button("Confirm and Send Email to School"):
        st.success(
            f"Notification and student email ({st.session_state.email}) successfully sent to the school administration!")
        st.session_state.current_page = "dashboard"
        st.rerun()

    if st.button("⬅ Back to Plans"):
        st.session_state.current_page = "plans"
        st.rerun()


# ---------------------------------------------------------
# DASHBOARD PAGE
# ---------------------------------------------------------
elif st.session_state.current_page == "dashboard":
    st.markdown(f"""
        <div class="header-card">
            <h1>Skill Nest — Dashboard</h1>
            <p>Welcome, <b>{st.session_state.user}</b>! | Plan: <b>{st.session_state.plan}</b></p>
        </div>
    """, unsafe_allow_html=True)

    grade_options = list(AP_SYLLABUS_DATABASE.keys())
    selected_grade_dropdown = st.selectbox(
        "Select Class Dropdown:",
        grade_options,
        index=grade_options.index(st.session_state.grade) if st.session_state.grade in grade_options else 0
    )

    if selected_grade_dropdown != st.session_state.grade:
        st.session_state.grade = selected_grade_dropdown
        st.rerun()

    st.divider()

    current_grade_data = AP_SYLLABUS_DATABASE.get(st.session_state.grade, [])

    # ---------------------------------------------------------
    # STUDY WITH AI SECTION (PREMIUM ONLY - GEMINI POWERED)
    # ---------------------------------------------------------
    if st.session_state.plan == "Premium":
        st.markdown("## 🤖 Study with AI (Gemini Powered)")
        st.info(
            "Ask any concept or topic from your curriculum below to receive an expert curriculum breakdown instantly.")

        ai_name = st.text_input("Name your Custom AI Study Partner:", value="AP Study Buddy")
        user_query = st.text_input(f"Ask {ai_name} anything regarding your {st.session_state.grade} AP syllabus:",
                                   placeholder=" write your question here! ")

        if user_query:
            with st.spinner(f"{ai_name} is thinking..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"""You are {ai_name}, an expert educational AI tutor for {st.session_state.grade} AP State Board students. 
                        Answer this student's question clearly and concisely: {user_query}

                        Format your response with:
                        - Core Formula / Lemma / Law (if applicable)
                        - Key Problem-Solving Strategy
                        - Exam Tip for maximum marks."""
                    )

                    st.markdown(f"""
                        <div class="ai-response-card">
                            <h3 style="color: #1a365d; margin-top: 0; margin-bottom: 10px;">💡 {ai_name} Curriculum Insight</h3>
                            <p style="line-height: 1.6; margin-bottom: 0;">{response.text}</p>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Connection error: {e}")

    st.markdown("## 📥 Download Study Materials")
    col1 = st.columns(1)[0]
    with col1:
        full_grade_pdf = generate_large_pdf(st.session_state.grade, st.session_state.board, st.session_state.plan,
                                            current_grade_data)
        st.download_button(
            label=f"📥 Download Full PDF Handbook ({st.session_state.grade})",
            data=full_grade_pdf,
            file_name=f"{st.session_state.grade.replace(' ', '_')}_AP_Handbook.pdf",
            mime="application/pdf",
        )

    st.divider()

    for idx, ch in enumerate(current_grade_data):
        st.markdown(f"### [{ch['subject']}] {ch['chapter']}")
        st.markdown(ch['detailed_notes'], unsafe_allow_html=True)
        st.divider()

    if st.button("Log out / Switch Account"):
        st.session_state.user = None
        st.session_state.plan = None
        st.session_state.current_page = "login"
