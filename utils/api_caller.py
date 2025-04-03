from fastapi import UploadFile  # ✅ Import UploadFile
from articles import surgical_device as s_d, diagnostic as dia

class ApiCaller:
    def __init__(self):
        self.analyzer_surgical = s_d.SurgicalDeviceAnalyzer()  # ✅ Ensure correct module reference
        self.analyzer_diagnostic = dia.DiagnosticAnalyzer()  # ✅ Ensure correct module reference

    def analyze_surgical_device(self, uploaded_file: UploadFile, device_name: str, technique: str):
        return self.analyzer_surgical.analyze_surgical_device(uploaded_file, device_name, technique)

    def analyze_diagnostic(self, uploaded_file: UploadFile, test_name: str, technique: str, sample_type: str, diagnostic_type: str):
        return self.analyzer_diagnostic.analyze_diagnostic(uploaded_file, test_name, technique, sample_type, diagnostic_type)
