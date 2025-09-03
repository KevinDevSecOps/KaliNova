"""
Sistema de reporting profesional con múltiples formatos
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import json

class AdvancedReporter:
    def generate_pdf_report(self, results: Dict, filename: str):
        """Generar reporte PDF profesional"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("KaliNova Security Report", styles['Title'])
        story.append(title)
        
        # Tabla de vulnerabilidades
        if 'vulnerabilities' in results:
            data = [['Tipo', 'Severidad', 'Descripción']]
            for vuln in results['vulnerabilities']:
                data.append([vuln.get('type', ''), vuln.get('severity', ''), vuln.get('description', '')])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#777777'),
                ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), '#eeeeee'),
            ]))
            story.append(table)
        
        doc.build(story)