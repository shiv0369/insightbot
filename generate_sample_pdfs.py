"""
Generates 3 fake quarterly reports that match the Superstore data.
This makes our RAG demo realistic — the reports talk about the same
regions, products, and trends our database contains.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

os.makedirs("data/reports", exist_ok=True)

REPORTS = {
    "Q1_2017_Report.pdf": {
        "title": "Superstore Quarterly Business Review — Q1 2017",
        "sections": [
            ("Executive Summary",
             "Q1 2017 marked a strong start to the fiscal year for Superstore. Total revenue reached $470,533, "
             "a 12% increase year-over-year. Profit margins held steady at 8.4%. The Technology category continued "
             "to lead growth, driven primarily by strong Phone and Copier sales in the West region."),
            
            ("Regional Performance",
             "The West region delivered exceptional results with $186,420 in sales, accounting for 39% of total "
             "company revenue. The East region followed with $145,300. The Central region saw a modest 3% decline "
             "due to seasonal slowdowns in office equipment purchases. The South region remained stable but flat, "
             "showing minimal growth over Q4 2016."),
            
            ("Product Category Insights",
             "Technology products generated $172,800 in revenue with healthy 15% margins. Office Supplies remained "
             "the volume leader at 60% of total orders, though margins were thinner at 6%. Furniture saw mixed results: "
             "Chairs and Tables performed well, but Bookcases continued to drag profitability with consistent losses."),
            
            ("Key Challenges",
             "Discount strategies in the Central region eroded profitability. Average discounts of 24% in Furniture "
             "led to several unprofitable transactions. Customer churn in the consumer segment increased slightly. "
             "Recommendation: tighten discount approval policies for orders above $500."),
        ]
    },
    
    "Q2_2017_Report.pdf": {
        "title": "Superstore Quarterly Business Review — Q2 2017",
        "sections": [
            ("Executive Summary",
             "Q2 2017 showed continued growth momentum with total revenue of $514,239, up 9% from Q1. Profit "
             "increased 14% quarter-over-quarter, driven by improved margins in the Technology category. The Corporate "
             "segment emerged as the fastest-growing customer group."),
            
            ("Regional Performance",
             "The West region continued its dominance with $201,890 in sales. The East region surged with a 22% "
             "growth rate, reaching $177,400 — the strongest quarterly growth in two years. This was primarily "
             "driven by new corporate accounts in New York and Boston. The South region rebounded with a 15% increase, "
             "while the Central region recovered modestly with 7% growth."),
            
            ("Customer Segment Analysis",
             "Corporate customers contributed 32% of revenue in Q2, up from 27% in Q1. Consumer segment remained "
             "the largest at 51%. Home Office showed slight contraction. The top 10 corporate customers accounted "
             "for 18% of total quarterly revenue, indicating customer concentration risk that should be monitored."),
            
            ("Operational Notes",
             "Shipping delays in May affected approximately 4% of orders, primarily in the East region due to a "
             "warehouse transition. The issue was resolved by mid-June. Customer satisfaction scores dipped slightly "
             "during this period but recovered by quarter end."),
        ]
    },
    
    "Q3_2017_Report.pdf": {
        "title": "Superstore Quarterly Business Review — Q3 2017",
        "sections": [
            ("Executive Summary",
             "Q3 2017 was a challenging quarter. Total revenue declined 6% to $483,107, primarily due to weakness "
             "in the East region and softness in Office Supplies. However, the Technology category continued to grow, "
             "and overall profit margins improved to 9.1%."),
            
            ("Regional Performance — Critical Analysis",
             "The East region experienced an unexpected 18% decline in sales, falling to $145,500. Root cause analysis "
             "identified three factors: (1) supply chain disruptions affecting Copier and Printer inventory throughout "
             "August, (2) loss of two major corporate accounts to competitors, and (3) extended shipping times due to "
             "the same warehouse transition issues that began in Q2. The West region remained strong at $208,400. "
             "Central and South regions performed in line with expectations."),
            
            ("Product Category Performance",
             "Technology grew 11% despite supply chain issues, led by Phone sales. Office Supplies dropped 14% — "
             "the steepest category decline in two years — primarily in Paper and Binders. Furniture remained "
             "challenged, with Bookcases producing $8,400 in losses. Chairs continued to be the bright spot in "
             "Furniture, with consistent profitability."),
            
            ("Action Plan for Q4",
             "Three priorities for Q4: (1) Restore East region performance through aggressive corporate outreach "
             "and a dedicated account recovery team, (2) Discontinue underperforming Bookcases SKUs and reallocate "
             "shelf space, (3) Resolve all remaining warehouse transition issues by October 15. Revenue target for "
             "Q4 is $580,000, representing 20% sequential growth."),
        ]
    },
}


def create_pdf(filename: str, content: dict):
    """Create a single PDF report."""
    filepath = os.path.join("data/reports", filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=0.7*inch, bottomMargin=0.7*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                  fontSize=18, textColor='#1F2937', spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                    fontSize=13, textColor='#4F46E5', spaceAfter=10, spaceBefore=14)
    body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'],
                                 fontSize=11, leading=16, spaceAfter=12)
    
    story = []
    story.append(Paragraph(content["title"], title_style))
    story.append(Spacer(1, 0.2*inch))
    
    for heading, body in content["sections"]:
        story.append(Paragraph(heading, heading_style))
        story.append(Paragraph(body, body_style))
    
    doc.build(story)
    print(f"   ✅ Created {filename}")


if __name__ == "__main__":
    print("📄 Generating sample reports...")
    
    for filename, content in REPORTS.items():
        create_pdf(filename, content)
    
    print(f"\n✅ All reports saved in data/reports/")