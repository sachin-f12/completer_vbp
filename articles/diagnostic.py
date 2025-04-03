from .base import ArticleAnalyzer
from utils import csv_utils
from run_analysis import run_openai_analysis_for_Influenza_diagnostic, run_openai_analysis_for_sars_diagnostic
from settings import BASE_DIR
import os

# Define common file paths
TEMP_PDF_PATH = os.path.join(BASE_DIR, "data", "temp.pdf")
FLU_CSV_PATH = os.path.join(BASE_DIR, "data", "flu.csv")
SARS_CSV_PATH = os.path.join(BASE_DIR, "data", "sars.csv")

class DiagnosticAnalyzer(ArticleAnalyzer):
    def analyze_diagnostic(self, pdf_file, test_name, technique, sample, diagnostic_type):
        """Analyzes a diagnostic test article and stores results in CSV."""

        # Save uploaded PDF file temporarily
        with open(TEMP_PDF_PATH, "wb") as f:
            f.write(pdf_file.file.read())  # Correct usage


        # Extract and clean text from the PDF
        extracted_text = self.extract_text_from_pdf(TEMP_PDF_PATH)
        cleaned_text = self.remove_unwanted_sections(extracted_text)

        # Choose analysis based on diagnostic type
        if diagnostic_type == "Influenza":
            analysis_result = run_openai_analysis_for_Influenza_diagnostic(cleaned_text, test_name, technique, sample)
            csv_path = FLU_CSV_PATH
            field_names = [
                "Reference", "Test Name", "Technique", "Sample", "n", 
                "InfluenzaABSympNAPositives", "InfluenzaABAsympPositives", "InfluenzaABPositives",
                "InfluenzaABNegatives", "InfluenzaBSympNAPositives", "InfluenzaBPositives",
                "InfluenzaBNegatives", "All True Positive Samples", "Negative Samples",
                "Influenza A Sensitivity/ PPA", "Influenza A Specificity/ NPA",
                "Influenza B Sensitivity/ PPA", "Influenza B Specificity/ NPA",
                "Influenza A/B (LDT) Ct Value Positive Threshold",
                "# Multiplex Differential Diagnoses Per Run", "Pathogen Sample Time to Result Hours",
                "Hands on Time (Instrument only) Hours", "Number of Steps Instrument only",
                "Percent who easily understood the user manual", "Percent of patients who found the test easy to use (as expected)",
                "Percent of patients who found the test very easy to use", "Percent who correctly interpreted the results",
                "Percent who were confident they could use the test at home"
            ]
        else:  # SARS-CoV-2 Diagnostic
            analysis_result = run_openai_analysis_for_sars_diagnostic(cleaned_text, test_name, technique, sample)
            csv_path = SARS_CSV_PATH
            field_names = [
                "Reference", "Test Name", "Technique", "Sample", "n",
                "COVIDSympNAPositives", "COVIDAsympPositives", "COVIDPositives",
                "COVIDNegatives", "SARS-CoV-2 Positive Percent Agreement",
                "SARS-CoV-2 Negative Percent Agreement", "SARS-CoV-2 Ct Value Positive Detection Cutoff",
                "SARS-CoV-2 Asymptomatic Sensitivity", "SARS-CoV-2 Symptomatic Sensitivity",
                "SARS-CoV-2 Asymptomatic Specificity", "SARS-CoV-2 Symptomatic Specificity",
                "SARS-CoV-2 Days Past Infection/Symptom Onset Sensitivity Day 0/2/6/10",
                "# Multiplex Differential Diagnoses Per Run", "Pathogen Sample Time to Result Hours",
                "Hands on Time (Instrument only) Hours", "Number of Steps Instrument only",
                "Percent who easily understood the user manual", "Percent of patients who found the test easy to use (as expected)",
                "Percent of patients who found the test very easy to use", "Percent who correctly interpreted the results",
                "Percent who were confident they could use the test at home"
            ]

        # Parse the AI response and structure data
        parsed_data = csv_utils.parse_response(analysis_result, pdf_file.filename)
        parsed_data["Test Name"] = test_name
        parsed_data["Technique"] = technique
        parsed_data["Sample"] = sample

        # Save results to CSV
        csv_utils.write_data_to_csv(parsed_data, csv_path, field_names)

        return analysis_result  # Return AI analysis output
