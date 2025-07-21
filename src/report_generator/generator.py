# Générateur de comptes rendus médicaux
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader
import json

import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
from pydicom.sr.codedict import codes
from pydicom.sr.coding import Code
from pydicom.sr.template import Template1500

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors

from ..config.settings import settings
from ..ai_engine.processor import AIResults, Finding

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Générateur de comptes rendus structurés"""
    
    def __init__(self):
        self.template_dir = Path(settings.report_template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        
        # Styles pour PDF
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        logger.info("Générateur de rapports initialisé")
    
    def _setup_custom_styles(self):
        """Configuration des styles personnalisés pour PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='FindingTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.darkred
        ))
        
        self.styles.add(ParagraphStyle(
            name='FindingText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8
        ))
    
    async def generate_report(self, dicom_ds: Dataset, ai_results: AIResults) -> Optional[Path]:
        """Génération du compte rendu principal"""
        try:
            logger.info(f"Génération du rapport pour: {ai_results.instance_uid}")
            
            # Choix du format selon la configuration
            if settings.report_output_format == "DICOM_SR":
                report_path = await self._generate_dicom_sr(dicom_ds, ai_results)
            elif settings.report_output_format == "PDF":
                report_path = await self._generate_pdf_report(dicom_ds, ai_results)
            else:
                # Génération des deux formats
                sr_path = await self._generate_dicom_sr(dicom_ds, ai_results)
                pdf_path = await self._generate_pdf_report(dicom_ds, ai_results)
                report_path = sr_path  # Retour du DICOM SR par défaut
            
            if report_path and report_path.exists():
                logger.info(f"Rapport généré avec succès: {report_path}")
                return report_path
            else:
                logger.error("Échec de la génération du rapport")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return None
    
    async def _generate_dicom_sr(self, dicom_ds: Dataset, ai_results: AIResults) -> Optional[Path]:
        """Génération d'un rapport DICOM Structured Report"""
        try:
            # Création du dataset SR
            sr_ds = Dataset()
            
            # Métadonnées DICOM obligatoires
            sr_ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.88.11"  # Basic Text SR
            sr_ds.SOPInstanceUID = generate_uid()
            sr_ds.StudyInstanceUID = dicom_ds.get('StudyInstanceUID', generate_uid())
            sr_ds.SeriesInstanceUID = generate_uid()
            sr_ds.Modality = "SR"
            sr_ds.SeriesNumber = "9999"
            sr_ds.InstanceNumber = "1"
            
            # Informations patient
            sr_ds.PatientName = dicom_ds.get('PatientName', 'ANONYME^PATIENT')
            sr_ds.PatientID = dicom_ds.get('PatientID', 'UNKNOWN')
            sr_ds.PatientBirthDate = dicom_ds.get('PatientBirthDate', '')
            sr_ds.PatientSex = dicom_ds.get('PatientSex', '')
            
            # Informations étude
            sr_ds.StudyDate = dicom_ds.get('StudyDate', datetime.now().strftime('%Y%m%d'))
            sr_ds.StudyTime = dicom_ds.get('StudyTime', datetime.now().strftime('%H%M%S'))
            sr_ds.AccessionNumber = dicom_ds.get('AccessionNumber', '')
            sr_ds.StudyDescription = dicom_ds.get('StudyDescription', 'Analyse IA')
            
            # Informations série
            sr_ds.SeriesDate = datetime.now().strftime('%Y%m%d')
            sr_ds.SeriesTime = datetime.now().strftime('%H%M%S')
            sr_ds.SeriesDescription = "Rapport d'analyse IA"
            
            # Contenu du rapport structuré
            sr_ds.ValueType = "CONTAINER"
            sr_ds.ConceptNameCodeSequence = [Dataset()]
            sr_ds.ConceptNameCodeSequence[0].CodeValue = "18782-3"
            sr_ds.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
            sr_ds.ConceptNameCodeSequence[0].CodeMeaning = "Radiology Report"
            
            # Construction du contenu
            content_sequence = []
            
            # Titre du rapport
            title_item = Dataset()
            title_item.ValueType = "TEXT"
            title_item.ConceptNameCodeSequence = [Dataset()]
            title_item.ConceptNameCodeSequence[0].CodeValue = "121111"
            title_item.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
            title_item.ConceptNameCodeSequence[0].CodeMeaning = "Summary"
            title_item.TextValue = self._generate_summary_text(ai_results)
            content_sequence.append(title_item)
            
            # Ajout des findings
            for i, finding in enumerate(ai_results.findings):
                finding_item = Dataset()
                finding_item.ValueType = "TEXT"
                finding_item.ConceptNameCodeSequence = [Dataset()]
                finding_item.ConceptNameCodeSequence[0].CodeValue = "121071"
                finding_item.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
                finding_item.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
                finding_item.TextValue = self._format_finding_text(finding)
                content_sequence.append(finding_item)
            
            # Conclusion
            conclusion_item = Dataset()
            conclusion_item.ValueType = "TEXT"
            conclusion_item.ConceptNameCodeSequence = [Dataset()]
            conclusion_item.ConceptNameCodeSequence[0].CodeValue = "121070"
            conclusion_item.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
            conclusion_item.ConceptNameCodeSequence[0].CodeMeaning = "Findings Summary"
            conclusion_item.TextValue = self._generate_conclusion(ai_results)
            content_sequence.append(conclusion_item)
            
            sr_ds.ContentSequence = content_sequence
            
            # Sauvegarde du fichier
            output_dir = Path(settings.data_directory) / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"SR_{ai_results.instance_uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dcm"
            output_path = output_dir / filename
            
            sr_ds.save_as(output_path, write_like_original=False)
            
            logger.info(f"Rapport DICOM SR généré: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération DICOM SR: {e}")
            return None
    
    async def _generate_pdf_report(self, dicom_ds: Dataset, ai_results: AIResults) -> Optional[Path]:
        """Génération d'un rapport PDF"""
        try:
            output_dir = Path(settings.data_directory) / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"Report_{ai_results.instance_uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = output_dir / filename
            
            # Création du document PDF
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            story = []
            
            # En-tête
            story.append(Paragraph("RAPPORT D'ANALYSE IA - RADIOLOGIE", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.5*cm))
            
            # Informations patient
            patient_data = [
                ['Patient:', dicom_ds.get('PatientName', 'ANONYME')],
                ['ID Patient:', dicom_ds.get('PatientID', 'UNKNOWN')],
                ['Date de naissance:', dicom_ds.get('PatientBirthDate', 'Inconnue')],
                ['Sexe:', dicom_ds.get('PatientSex', 'Inconnu')],
                ['Date d\'étude:', dicom_ds.get('StudyDate', 'Inconnue')],
                ['Modalité:', ai_results.modality],
                ['Temps de traitement:', f"{ai_results.processing_time:.2f}s"]
            ]
            
            patient_table = Table(patient_data, colWidths=[4*cm, 8*cm])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 1*cm))
            
            # Résumé
            story.append(Paragraph("RÉSUMÉ", self.styles['Heading2']))
            summary_text = self._generate_summary_text(ai_results)
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 0.5*cm))
            
            # Findings détaillés
            if ai_results.findings:
                story.append(Paragraph("ANOMALIES DÉTECTÉES", self.styles['Heading2']))
                
                for i, finding in enumerate(ai_results.findings, 1):
                    story.append(Paragraph(f"Anomalie {i}: {finding.type.replace('_', ' ').title()}", 
                                         self.styles['FindingTitle']))
                    
                    finding_details = [
                        f"<b>Description:</b> {finding.description}",
                        f"<b>Confiance:</b> {finding.confidence:.2%}",
                        f"<b>Sévérité:</b> {finding.severity.title()}",
                        f"<b>Localisation:</b> x={finding.location[0]}, y={finding.location[1]}, "
                        f"largeur={finding.location[2]}, hauteur={finding.location[3]}"
                    ]
                    
                    if finding.measurements:
                        measurements_text = ", ".join([f"{k}: {v}" for k, v in finding.measurements.items()])
                        finding_details.append(f"<b>Mesures:</b> {measurements_text}")
                    
                    for detail in finding_details:
                        story.append(Paragraph(detail, self.styles['FindingText']))
                    
                    story.append(Spacer(1, 0.3*cm))
            else:
                story.append(Paragraph("AUCUNE ANOMALIE DÉTECTÉE", self.styles['Heading2']))
                story.append(Paragraph("L'analyse IA n'a détecté aucune anomalie significative dans cette image.", 
                                     self.styles['Normal']))
            
            story.append(Spacer(1, 1*cm))
            
            # Conclusion
            story.append(Paragraph("CONCLUSION", self.styles['Heading2']))
            conclusion_text = self._generate_conclusion(ai_results)
            story.append(Paragraph(conclusion_text, self.styles['Normal']))
            
            # Pied de page
            story.append(Spacer(1, 1*cm))
            footer_text = f"""<i>Rapport généré automatiquement par le système d'IA médicale.<br/>
            Version du modèle: {ai_results.model_version}<br/>
            Date de génération: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}<br/>
            Ce rapport doit être validé par un radiologue qualifié.</i>"""
            story.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Construction du PDF
            doc.build(story)
            
            logger.info(f"Rapport PDF généré: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération PDF: {e}")
            return None
    
    def _generate_summary_text(self, ai_results: AIResults) -> str:
        """Génération du texte de résumé"""
        if not ai_results.findings:
            return f"Analyse IA de l'image {ai_results.modality} terminée. Aucune anomalie significative détectée."
        
        findings_count = len(ai_results.findings)
        high_severity = sum(1 for f in ai_results.findings if f.severity == 'high')
        
        summary = f"Analyse IA de l'image {ai_results.modality} terminée. "
        summary += f"{findings_count} anomalie(s) détectée(s)"
        
        if high_severity > 0:
            summary += f", dont {high_severity} de sévérité élevée"
        
        summary += f". Confiance globale: {ai_results.overall_confidence:.2%}."
        
        return summary
    
    def _format_finding_text(self, finding: Finding) -> str:
        """Formatage du texte d'une anomalie"""
        text = f"{finding.description} "
        text += f"Localisation: ({finding.location[0]}, {finding.location[1]}). "
        text += f"Sévérité: {finding.severity}. "
        
        if finding.measurements:
            measurements = ", ".join([f"{k}: {v}" for k, v in finding.measurements.items()])
            text += f"Mesures: {measurements}."
        
        return text
    
    def _generate_conclusion(self, ai_results: AIResults) -> str:
        """Génération de la conclusion"""
        if not ai_results.findings:
            return "L'analyse automatisée n'a révélé aucune anomalie significative. " \
                   "Un contrôle par un radiologue reste recommandé pour validation."
        
        high_severity_findings = [f for f in ai_results.findings if f.severity == 'high']
        
        if high_severity_findings:
            conclusion = "ATTENTION: Des anomalies de sévérité élevée ont été détectées. "
            conclusion += "Une évaluation urgente par un radiologue est fortement recommandée. "
        else:
            conclusion = "Des anomalies ont été détectées mais nécessitent une validation par un radiologue. "
        
        conclusion += f"Confiance globale du système: {ai_results.overall_confidence:.2%}. "
        conclusion += "Ce rapport automatisé ne remplace pas l'expertise médicale humaine."
        
        return conclusion

    async def create_template_files(self):
        """Création des fichiers de template par défaut"""
        try:
            # Template HTML pour rapport
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Rapport d'Analyse IA</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; }
        .finding { border-left: 3px solid #007bff; padding-left: 10px; margin: 10px 0; }
        .high-severity { border-left-color: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Rapport d'Analyse IA - {{ modality }}</h1>
        <p>Patient: {{ patient_name }} ({{ patient_id }})</p>
        <p>Date: {{ study_date }}</p>
    </div>
    
    <h2>Résumé</h2>
    <p>{{ summary }}</p>
    
    {% if findings %}
    <h2>Anomalies Détectées</h2>
    {% for finding in findings %}
    <div class="finding {% if finding.severity == 'high' %}high-severity{% endif %}">
        <h3>{{ finding.type.replace('_', ' ').title() }}</h3>
        <p>{{ finding.description }}</p>
        <p><strong>Confiance:</strong> {{ "%.2f%%"|format(finding.confidence * 100) }}</p>
        <p><strong>Sévérité:</strong> {{ finding.severity.title() }}</p>
    </div>
    {% endfor %}
    {% endif %}
    
    <h2>Conclusion</h2>
    <p>{{ conclusion }}</p>
</body>
</html>
            """
            
            template_path = self.template_dir / "report_template.html"
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            logger.info(f"Template HTML créé: {template_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des templates: {e}")