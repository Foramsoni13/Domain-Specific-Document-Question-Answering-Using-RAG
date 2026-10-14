"""
Generator for domain-specific test documents:
1. Apex University Academic Regulations & Examination Policies (2025-2026)
2. NexaCorp Global Employee HR Handbook & Benefits Manual (2025)
3. Metro City Municipal Corporation Citizen Services Circular (No. 44/2025)

Generates both clean text and multi-page formatted PDF files.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCUMENTS = {
    "university_academic_regulations_2025": {
        "title": "APEX TECHNICAL UNIVERSITY - ACADEMIC REGULATIONS & EXAMINATION POLICIES (2025-2026)",
        "subtitle": "Office of the Dean of Academic Affairs | Circular No. ATU/RO/2025/1102",
        "sections": [
            {
                "page": 1,
                "heading": "Section 1: General Academic Structure & Credit Framework",
                "content": """1.1 Academic Calendar & Semesters
The academic year at Apex Technical University is partitioned into two regular semesters: Autumn Semester (August to December) and Spring Semester (January to May), supplemented by an optional 6-week Summer Term (June to July). Each standard semester spans a minimum of 90 instructional working days excluding examinations.

1.2 Credit Definition and Distribution
One academic credit is formally defined as:
(a) One hour of classroom lecture (L) per week per semester = 1.0 Credit
(b) One hour of tutorial (T) per week per semester = 1.0 Credit
(c) Two hours of laboratory or studio practical work (P) per week per semester = 1.0 Credit
Undergraduate degree students in Bachelor of Technology (B.Tech) must complete a cumulative minimum of 160 credits to qualify for graduation. For B.Tech with Academic Honors, students must earn an additional 18 honors credits through advanced electives and a supervised capstone research thesis.

1.3 Maximum Allowable Duration
A student registered in a 4-year degree programme must successfully complete all requirements within a maximum time ceiling of 6 consecutive academic years. Failure to complete all degree requirements within this 6-year window results in automatic cancellation of academic registration."""
            },
            {
                "page": 2,
                "heading": "Section 2: Attendance Requirements & Condone Exceptions",
                "content": """2.1 Mandatory Attendance Threshold
A student must maintain a minimum attendance of 75% in aggregate across all lectures, tutorials, and practical laboratory sessions in each registered course to be eligible to appear for the End-Semester Examination.

2.2 Medical Condonation Policy
If a student's attendance falls between 65% and 74.9% due to verified serious illness, hospitalization, or representing the University in national/international academic or sports events, condonation of shortage of attendance may be granted by the Dean of Academic Affairs. To claim medical condonation:
(a) The student must submit an official medical certificate issued by a registered medical practitioner along with discharge summaries within 5 working days of resuming classes.
(b) The departmental faculty advisor and Head of Department (HOD) must verify and forward the application.
(c) A non-refundable condonation processing fee of $50 per course is levied upon approval.
Attendance falling below 65% under any circumstances cannot be condoned, and the student will be awarded an 'FA' (Failure due to Attendance) grade, mandating course re-registration."""
            },
            {
                "page": 3,
                "heading": "Section 3: Grading Scale, CGPA Calculation, and Promotion",
                "content": """3.1 10-Point Letter Grading System
Performance in each course is evaluated on a 10-point letter scale:
• Grade 'O' (Outstanding): 10 Grade Points (Marks >= 90%)
• Grade 'A+' (Excellent): 9 Grade Points (Marks 80% to 89%)
• Grade 'A' (Very Good): 8 Grade Points (Marks 70% to 79%)
• Grade 'B+' (Good): 7 Grade Points (Marks 60% to 69%)
• Grade 'B' (Above Average): 6 Grade Points (Marks 50% to 59%)
• Grade 'C' (Average / Pass): 5 Grade Points (Marks 40% to 49%)
• Grade 'F' (Fail): 0 Grade Points (Marks < 40%)
• Grade 'I' (Incomplete due to authorized medical emergency during final exam)
• Grade 'FA' (Fail due to Attendance): 0 Grade Points

3.2 Minimum SGPA and CGPA Promotion Criteria
A student is eligible for progression to the subsequent academic year provided:
(a) Minimum Cumulative Grade Point Average (CGPA) of 5.0 is maintained at the conclusion of each academic year.
(b) A student can carry over a maximum of 4 uncleared backlog courses (F grades) into the 3rd year, and a maximum of 2 backlogs into the final (4th) year."""
            },
            {
                "page": 4,
                "heading": "Section 4: Re-evaluation, Grievances, and Academic Integrity",
                "content": """4.1 Answer Script Verification and Re-evaluation
A student dissatisfied with their grade in the End-Semester Examination may apply for formal re-evaluation within 14 calendar days of result publication:
• Step 1: Request photocopy/inspection of evaluated answer script upon payment of $20 per course.
• Step 2: If a scoring discrepancy exceeds 5% of total marks, request blind re-evaluation by an external examiner with a fee of $60 per course. If the revised score varies by more than 10%, the higher score is assigned and 50% of the re-evaluation fee is refunded.

4.2 Academic Plagiarism and Dishonesty Penalties
All student project reports, seminar papers, and capstone theses are subjected to similarity checking via Turnitin:
• Similarity Level 0 (up to 10%): Permissible with minor citations.
• Similarity Level 1 (10% to 25%): Student is required to revise and resubmit within 7 days.
• Similarity Level 2 (25% to 50%): Disqualification from the current semester's submission and deduction of one full letter grade.
• Similarity Level 3 (Above 50% or exam cheating): Zero marks awarded, suspension for one full academic year, and formal disciplinary notice on academic transcript."""
            }
        ]
    },
    "employee_hr_benefits_handbook": {
        "title": "NEXACORP GLOBAL EMPLOYEE HR POLICY & BENEFITS MANUAL (2025)",
        "subtitle": "Human Resources Management Division | Document Reference: HR-POL-2025-V3",
        "sections": [
            {
                "page": 1,
                "heading": "Section 1: Employment Terms, Work Hours, and Hybrid Policy",
                "content": """1.1 Probationary Period
All newly hired full-time regular employees undergo a mandatory probationary period of six (6) months from their start date. Performance is formally evaluated at the 90-day and 180-day milestones. Upon successful completion and manager sign-off, confirmation is issued in writing. NexaCorp reserves the right to extend probation by up to an additional three (3) months if performance standards are not fully satisfied.

1.2 Working Hours and Core Collaboration Hours
Standard working hours are 40 hours per week, Monday through Friday. Core collaboration hours during which all employees must be reachable and available for meetings are 10:00 AM to 3:00 PM in their respective local regional time zone.

1.3 Hybrid Workplace Guidelines
Eligible employees in technical, product, and administrative tracks may participate in the Hybrid Working Program:
• Minimum Requirement: Employees must work on-site at a designated corporate office at least two (2) specified days per week (typically Tuesdays and Thursdays).
• Remote Workspace Allowance: Eligible hybrid employees receive a one-time remote home office setup stipend of $800 to purchase ergonomic furniture, monitors, or accessories."""
            },
            {
                "page": 2,
                "heading": "Section 2: Paid Time Off (PTO), Sick Leave, and Parental Leave",
                "content": """2.1 Paid Annual Vacation Leave
Full-time employees accrue 20 working days of Paid Time Off (PTO) per calendar year, accrued proportionally on a monthly basis (1.67 days per month). A maximum of 8 unused PTO days can be rolled over into the succeeding calendar year. Any unused PTO exceeding 8 days as of December 31st will expire without monetary payout.

2.2 Sick and Wellness Leave
Employees receive 10 dedicated days of paid sick leave per year, available from day one. Absences exceeding three (3) consecutive business days require submission of a verified doctor's medical certificate to HR Operations.

2.3 Comprehensive Parental Leave
NexaCorp provides 16 consecutive weeks of 100% paid primary caregiver parental leave to all employees who have completed at least twelve (12) continuous months of employment. Secondary caregivers receive 6 consecutive weeks of 100% paid leave. Parental leave must be taken within twelve (12) months following birth, adoption, or foster placement."""
            },
            {
                "page": 3,
                "heading": "Section 3: Health Insurance, Wellness Benefits, and Retirement",
                "content": """3.1 Medical, Dental, and Vision Coverage
NexaCorp covers 90% of monthly health insurance premium costs for employees and 75% of premium costs for eligible dependents:
• Medical Plan: In-network annual deductible is $500 per individual and $1,000 per family. Maximum out-of-pocket limit is $3,500.
• Dental Coverage: 100% preventive care covered; 80% basic procedures; annual maximum dental benefit of $2,500 per covered member.
• Vision Coverage: Annual comprehensive eye exam covered 100%; $200 biennial hardware allowance for prescription glasses or contact lenses.

3.2 401(k) Retirement Savings Match
Employees can enroll in the corporate 401(k) plan immediately upon hire. NexaCorp matches 100% of employee contributions up to the first 4% of eligible annual salary, and 50% on the next 2% contributed (maximum effective company match of 5%). Company matching funds follow a 2-year graded vesting schedule: 50% after Year 1, 100% after Year 2."""
            },
            {
                "page": 4,
                "heading": "Section 4: Professional Development, Travel Reimbursement, and Notice",
                "content": """4.1 Professional Development & Tuition Subsidy
To encourage lifelong learning, NexaCorp reimburses up to $2,500 per calendar year per employee for approved external certifications, university courses, and technical conferences. Coursework must be directly aligned with the employee's current or anticipated future career path and requires prior manager approval.

4.2 Business Travel Expense Policy
Employees traveling on official company business are entitled to reimbursement under corporate guidelines:
• Hotel Accommodation: Domestic ceiling of $220/night; international ceiling of $320/night.
• Daily Meal Per Diem: Up to $75 per day for domestic travel; up to $100 per day for international travel.
• Flights exceeding 6 continuous hours qualify for Premium Economy. Business Class travel is strictly reserved for transcontinental flights exceeding 10 hours with VP-level authorization.

4.3 Resignation and Notice Period
Regular confirmed employees who choose to resign must provide a minimum notice period:
• Individual Contributors (IC1 to IC3): 2 weeks written notice.
• Senior Engineers, Managers, and Directors: 4 weeks written notice.
• Vice Presidents and Executives: 8 weeks written notice."""
            }
        ]
    },
    "municipal_citizen_services_circular": {
        "title": "METRO CITY MUNICIPAL CORPORATION - CITIZEN SERVICES & COMPLIANCE CIRCULAR (2025)",
        "subtitle": "Department of Urban Administration & Public Welfare | Circular No. MCMC/PUB/2025/88",
        "sections": [
            {
                "page": 1,
                "heading": "Section 1: Residential Property Tax Assessment & Rebate Schemes",
                "content": """1.1 Annual Property Tax Deadlines
The property tax cycle for Metro City corresponds to the financial year (April 1 to March 31). Annual property tax demands are issued on May 1st each year. Taxes may be paid in a single lump sum or in two equal bi-annual installments due on June 30th and December 31st.

1.2 Early Payment and Green Energy Rebates
Citizens can avail of substantial financial rebates under certified civic initiatives:
(a) Early Bird Incentive: An immediate 10% rebate on total net property tax is awarded if the entire annual assessment is settled before June 30th.
(b) Rainwater Harvesting Rebate: Properties with certified, functional rainwater harvesting percolation pits receive a recurring 5% annual rebate on property tax.
(c) Solar Rooftop Rebate: Residential buildings equipped with grid-tied solar photovoltaic installations of at least 3 kW capacity receive an additional 6% rebate.
The maximum combined rebate under all municipal incentive programs shall not exceed 20% of gross property tax liability. Late payments settled after March 31st incur penal interest at 1.5% per month compounded quarterly."""
            },
            {
                "page": 2,
                "heading": "Section 2: Building Plan Sanction and Construction Permits",
                "content": """2.1 Residential Building Permit Turnaround
Under the Fast-Track Municipal Citizen Charter:
• Low-Risk Residential Plots (up to 200 sq. meters, max height 10 meters): Automatic deemed online approval generated within 7 business days upon submission of registered architect certification.
• Standard Residential Plots (201 to 500 sq. meters): Mandatory review turnaround is 21 working days. If no objection or defect notice is communicated within 21 working days, deemed sanction is legally applicable.
• Commercial and High-Rise Structures: Multi-departmental scrutiny (Fire Safety, Water Board, Traffic Police) completed within 45 working days.

2.2 Tree Preservation and Felling Regulations
No citizen or contractor may fell any mature tree (trunk circumference > 30 cm) on private or public land without prior written approval from the Metro City Tree Officer:
• Mandatory Compensatory Plantation: The applicant must plant ten (10) native saplings for every single tree felled and maintain them for three years.
• Unauthorized Felling Penalty: Violators will face a non-bailable civil penalty of $500 per tree plus mandatory restorative replantation."""
            },
            {
                "page": 3,
                "heading": "Section 3: Drinking Water Connections, Waste Management & Grievance Redressal",
                "content": """3.1 New Potable Water Supply Connection
Citizens applying for a domestic water connection must register on the Citizen Portal:
• Application Fee: $25 non-refundable verification charge.
• Connection Deposit: $150 refundable infrastructure security deposit.
• Meter Installation Guarantee: Water line tapping and smart digital meter installation must be completed within 14 calendar days of deposit confirmation.

3.2 Municipal Solid Waste Segregation Mandate
All households and commercial establishments are legally required to segregate garbage at source into three color-coded bins:
• Green Bin: Wet Biodegradable organic food waste.
• Blue Bin: Dry Recyclable paper, plastic, metals, and glass.
• Red Bin: Domestic hazardous and sanitary waste.
Non-segregated waste will not be collected by municipal sanitation vehicles. Repeat non-compliance after two formal written warnings attracts a fine of $25 for the first violation and $50 for each subsequent breach.

3.3 Citizen Grievance Escalation Hierarchy
Civic service complaints (water supply failure, street lighting, pothole repair) logged on the Helpline (1800-444-MCMC) follow a strict 3-tier Service Level Agreement (SLA):
• Level 1: Ward Field Engineer — Resolution window: 48 hours.
• Level 2: Executive Municipal Engineer — Escalation triggered if unresolved in 48 hours; resolution window: 72 hours.
• Level 3: Municipal Commissioner Public Hearing — Direct intervention every Wednesday 10:00 AM to 1:00 PM for grievances unresolved past 7 days."""
            }
        ]
    }
}

def create_text_files(base_dir):
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    for doc_key, doc_data in DOCUMENTS.items():
        txt_path = os.path.join(raw_dir, f"{doc_key}.txt")
        lines = [
            f"================================================================================",
            f"{doc_data['title']}",
            f"{doc_data['subtitle']}",
            f"================================================================================\n"
        ]
        for sec in doc_data["sections"]:
            lines.append(f"--- [PAGE {sec['page']}] ---")
            lines.append(f"{sec['heading']}\n")
            lines.append(f"{sec['content']}\n")
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Created text file: {txt_path}")

def create_pdf_files(base_dir):
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=14
    )
    heading_style = ParagraphStyle(
        'DocSectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8
    )
    footer_style = ParagraphStyle(
        'DocFooter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1
    )

    for doc_key, doc_data in DOCUMENTS.items():
        pdf_path = os.path.join(raw_dir, f"{doc_key}.pdf")
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        story = []
        for i, sec in enumerate(doc_data["sections"]):
            if i > 0:
                story.append(PageBreak())
            
            # Document header on each page
            story.append(Paragraph(doc_data["title"], title_style))
            story.append(Paragraph(f"{doc_data['subtitle']} | Page {sec['page']}", subtitle_style))
            story.append(Spacer(1, 8))
            
            # Section header
            story.append(Paragraph(sec["heading"], heading_style))
            story.append(Spacer(1, 6))
            
            # Body text paragraphs
            paragraphs = sec["content"].strip().split("\n\n")
            for p_text in paragraphs:
                clean_p = p_text.replace("\n", " ").strip()
                story.append(Paragraph(clean_p, body_style))
                story.append(Spacer(1, 4))
            
            story.append(Spacer(1, 15))
            story.append(Paragraph(f"Official Document — {doc_data['title']} — Page {sec['page']}", footer_style))
        
        doc.build(story)
        print(f"Created PDF document: {pdf_path}")

if __name__ == "__main__":
    base = "/Users/foram/Desktop/nlp"
    create_text_files(base)
    create_pdf_files(base)
    print("All sample domain documents successfully generated.")
