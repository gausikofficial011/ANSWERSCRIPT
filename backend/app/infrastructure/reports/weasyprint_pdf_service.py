"""
infrastructure/reports/weasyprint_pdf_service.py — PDF Generation Service
"""

from __future__ import annotations
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class WeasyPrintPDFService:
    """
    Infrastructure Service: Renders Jinja2 HTML templates and compiles them to PDF bytes via WeasyPrint.
    This service is isolated from database models, repositories, or business rules.
    """

    def __init__(self, templates_dir: str | None = None) -> None:
        if templates_dir is None:
            # Default to the templates/ subdirectory relative to this file
            templates_dir = str(Path(__file__).parent.resolve() / "templates")
        
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def generate_pdf(self, template_name: str, context: dict) -> bytes:
        """
        Compiles the Jinja2 template and generates PDF bytes in memory.
        """
        template = self.env.get_template(template_name)
        html_content = template.render(**context)
        
        # Import WeasyPrint HTML locally inside the method to allow testing 
        # on environments without GTK3 system libraries.
        from weasyprint import HTML
        
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
