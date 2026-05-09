import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def get_next_session_date():
    today = datetime.now()
    days_ahead = 0
    while True:
        candidate = today + timedelta(days=days_ahead)
        if candidate.weekday() in [3, 6]:
            return candidate.strftime("%b %d")
        days_ahead += 1

def calculate_streaks(df):
    if df.empty or 'status' not in df.columns or 'player' not in df.columns: 
        return pd.DataFrame(columns=["Player", "Max Streak"])
    
    streaks = []
    for player in df['player'].unique():
        p_df = df[df['player'] == player]
        if 'created_at' in p_df.columns: 
            p_df = p_df.sort_values('created_at')
        
        max_streak = 0
        current_streak = 0
        for status in p_df['status']:
            if status == "Available":
                current_streak += 1
                if current_streak > max_streak: 
                    max_streak = current_streak
            else:
                current_streak = 0
        streaks.append({"Player": player, "Max Streak": max_streak})
        
    return pd.DataFrame(streaks).sort_values(by="Max Streak", ascending=False).reset_index(drop=True)

def create_pdf(df, title="JVC Attendance Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [df.columns.to_list()] + df.values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#059669")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f1f5f9")]),
    ]))
    elements.append(t)
    doc.build(elements)
    return buffer.getvalue()