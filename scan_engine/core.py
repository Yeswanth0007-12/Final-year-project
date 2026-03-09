import uuid
from typing import List
from datetime import datetime
from scan_engine.models import ScanResult, ScanStatus, Vulnerability
from scan_engine.scanners.bandit_scanner import BanditScanner
from scan_engine.scanners.semgrep_scanner import SemgrepScanner
from scan_engine.intel.enrichment import EnrichmentService
from scan_engine.alerts import AlertService, AlertRecord
from scan_engine.audit import AuditService, SystemAudit

# Import unified database schema from server
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import SessionLocal, Vulnerability as UnifiedVulnerability, ScanSession, trigger_pipeline_update

class ScanEngine:
    def __init__(self):
        self.scanners = [
            BanditScanner(),
        ]
        
        # Check if semgrep is available
        import shutil
        if shutil.which("semgrep"):
            self.scanners.append(SemgrepScanner())
        # No longer need separate database - using unified schema
        self.enricher = EnrichmentService()
        self.alert_service = AlertService()
        self.audit_service = AuditService()

    def run_scan(self, target_path: str, scan_type: str = "manual") -> ScanSession:
        scan_id = str(uuid.uuid4())
        
        db = SessionLocal()
        try:
            # Create scan session in unified database
            scan_session = ScanSession(
                total_files_scanned=0,
                total_vulnerabilities=0,
                overall_risk_score=0
            )
            db.add(scan_session)
            db.commit()
            db.refresh(scan_session)
            
            self.audit_service.log_event("SCAN", f"Started diagnostic scan on target: {target_path}", resource_id=str(scan_session.id))
            
            all_vulnerabilities: List[Vulnerability] = []
            
            for scanner in self.scanners:
                try:
                    findings = scanner.scan(target_path)
                    all_vulnerabilities.extend(findings)
                except Exception as e:
                    print(f"Error executing {scanner.name}: {e}")

            severity_map = {}
            findings_saved = 0
            
            for vuln in all_vulnerabilities:
                try:
                    # Unified deduplication logic: (website_name, line_number, vulnerability_type)
                    # Use file_name as website_name for consistency
                    website_name = os.path.basename(vuln.file_path)
                    
                    # Check for existing record using unified deduplication key
                    existing = db.query(UnifiedVulnerability).filter(
                        UnifiedVulnerability.website_name == website_name,
                        UnifiedVulnerability.line_number == vuln.line_number,
                        UnifiedVulnerability.vulnerability_type == vuln.name
                    ).first()
                    
                    if existing:
                        continue

                    # Create unified vulnerability record
                    unified_vuln = UnifiedVulnerability(
                        id=f"SCAN-{uuid.uuid4().hex[:8]}",
                        scan_session_id=scan_session.id,
                        website_name=website_name,
                        url=vuln.file_path,
                        line_number=vuln.line_number,
                        vulnerability_type=vuln.name,
                        severity=vuln.severity.upper(),
                        code_snippet=vuln.code[:500] if vuln.code else f"<{vuln.name}> detected",
                        status="DETECTED",
                        risk_score=10.0 if vuln.severity.upper() == "HIGH" else 5.0,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    # Severity tracking
                    sev = vuln.severity.upper()
                    severity_map[sev] = severity_map.get(sev, 0) + 1
                    
                    if sev in ["CRITICAL", "HIGH"]:
                        self.alert_service.trigger_alert(sev, f"Detected {sev} vulnerability: {vuln.name} in {vuln.file_path}")

                    db.add(unified_vuln)
                    findings_saved += 1
                    scan_session.total_vulnerabilities += 1
                    scan_session.overall_risk_score += unified_vuln.risk_score
                    
                except Exception as e:
                    print(f"Error saving vulnerability {vuln.id}: {e}")
            
            # Commit all findings
            db.commit()
            trigger_pipeline_update()
            
            self.audit_service.log_event("SCAN", f"Diagnostic scan sequence terminated. Findings: {findings_saved}", resource_id=str(scan_session.id))
            
            return scan_session
            
        finally:
            db.close()
