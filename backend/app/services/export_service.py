from typing import Dict, Any
import pandas as pd
import json
from io import BytesIO
from fastapi import HTTPException
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ExportService:
    """Service for exporting reports in various formats."""
    
    def export_report(self, data: Dict[str, Any], format: str, name: str) -> BytesIO:
        """
        Export report data in the specified format.
        
        Args:
            data: The report data to export
            format: The export format (csv, json, xlsx, pdf)
            name: The name of the report
            
        Returns:
            BytesIO object containing the exported file
        """
        if format == 'csv':
            return self._export_csv(data)
        elif format == 'json':
            return self._export_json(data)
        elif format == 'xlsx':
            return self._export_excel(data)
        elif format == 'pdf':
            return self._export_pdf(data, name)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    def _export_csv(self, data: Dict[str, Any]) -> BytesIO:
        """Export data as CSV."""
        output = BytesIO()
        
        # Convert data to DataFrame
        df = self._prepare_dataframe(data)
        
        # Write to CSV
        df.to_csv(output, index=False)
        output.seek(0)
        return output

    def _export_json(self, data: Dict[str, Any]) -> BytesIO:
        """Export data as JSON."""
        output = BytesIO()
        
        # Write JSON data
        json.dump(data, output, indent=2)
        output.seek(0)
        return output

    def _export_excel(self, data: Dict[str, Any]) -> BytesIO:
        """Export data as Excel."""
        output = BytesIO()
        
        # Create Excel workbook
        workbook = xlsxwriter.Workbook(output)
        
        # Add worksheets for each section
        for section_name, section_data in data.items():
            worksheet = workbook.add_worksheet(section_name)
            
            # Write headers
            if isinstance(section_data, dict):
                headers = list(section_data.keys())
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header)
                
                # Write data
                for row, (key, value) in enumerate(section_data.items(), start=1):
                    worksheet.write(row, 0, key)
                    worksheet.write(row, 1, str(value))
            elif isinstance(section_data, list):
                if section_data:
                    headers = list(section_data[0].keys())
                    for col, header in enumerate(headers):
                        worksheet.write(0, col, header)
                    
                    # Write data
                    for row, item in enumerate(section_data, start=1):
                        for col, key in enumerate(headers):
                            worksheet.write(row, col, str(item.get(key, '')))
        
        workbook.close()
        output.seek(0)
        return output

    def _export_pdf(self, data: Dict[str, Any], name: str) -> BytesIO:
        """Export data as PDF."""
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title
        elements.append(Paragraph(name, styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Add each section
        for section_name, section_data in data.items():
            elements.append(Paragraph(section_name, styles['Heading1']))
            elements.append(Spacer(1, 12))
            
            if isinstance(section_data, dict):
                # Create table for dictionary data
                table_data = [[key, str(value)] for key, value in section_data.items()]
                table = Table(table_data, colWidths=[200, 300])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
            elif isinstance(section_data, list):
                # Create table for list data
                if section_data:
                    headers = list(section_data[0].keys())
                    table_data = [headers] + [[str(item.get(key, '')) for key in headers] for item in section_data]
                    table = Table(table_data, colWidths=[100] * len(headers))
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(table)
            
            elements.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(elements)
        output.seek(0)
        return output

    def _prepare_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Convert data to pandas DataFrame."""
        # Flatten nested dictionaries
        flat_data = {}
        for section_name, section_data in data.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    flat_data[f"{section_name}_{key}"] = value
            elif isinstance(section_data, list):
                for i, item in enumerate(section_data):
                    for key, value in item.items():
                        flat_data[f"{section_name}_{i}_{key}"] = value
        
        return pd.DataFrame([flat_data]) 