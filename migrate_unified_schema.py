"""
Database Migration Script
Migrates VulnerabilityRecord entries to unified vulnerabilities table
"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import SessionLocal, Vulnerability, ScanSession
from scan_engine.intel.db import get_session
from scan_engine.intel.models import VulnerabilityRecord, VulnerabilityStatus


def migrate_vulnerability_records():
    """
    Migrate all VulnerabilityRecord entries to the unified vulnerabilities table
    """
    print("[MIGRATION] Starting database schema migration...")
    
    server_db = SessionLocal()
    migrated_count = 0
    skipped_count = 0
    
    try:
        with get_session() as scan_db:
            # Get all VulnerabilityRecord entries
            vuln_records = scan_db.query(VulnerabilityRecord).all()
            print(f"[MIGRATION] Found {len(vuln_records)} VulnerabilityRecord entries to migrate")
            
            for record in vuln_records:
                # Check if already exists in unified table
                existing = server_db.query(Vulnerability).filter(
                    Vulnerability.website_name == record.file_name,
                    Vulnerability.line_number == int(record.vulnerable_lines.split(',')[0]) if record.vulnerable_lines else 0,
                    Vulnerability.vulnerability_type == record.vulnerability_type
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Map VulnerabilityStatus to unified status
                status_mapping = {
                    VulnerabilityStatus.DETECTED: "DETECTED",
                    VulnerabilityStatus.AI_FIX_GENERATED: "PATCH_APPLIED",
                    VulnerabilityStatus.VALIDATED: "VALIDATING",
                    VulnerabilityStatus.FIXED: "FIXED",
                    VulnerabilityStatus.REJECTED: "FAILED"
                }
                
                unified_status = status_mapping.get(record.status, "DETECTED")
                
                # Create unified vulnerability entry
                unified_vuln = Vulnerability(
                    id=record.id,
                    website_name=record.file_name,
                    url=record.file_path,
                    line_number=int(record.vulnerable_lines.split(',')[0]) if record.vulnerable_lines else 0,
                    vulnerability_type=record.vulnerability_type,
                    severity=record.severity,
                    code_snippet=record.full_code[:500] if record.full_code else f"<{record.vulnerability_type}> detected",
                    patch_code=record.ai_fix_code,
                    suggested_fix=record.remediation_guidance,
                    status=unified_status,
                    decision_score=record.exploitability,
                    risk_score=record.risk_score,
                    patch_explanation=record.ai_explanation,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                
                server_db.add(unified_vuln)
                migrated_count += 1
            
            server_db.commit()
            print(f"[MIGRATION] Successfully migrated {migrated_count} entries")
            print(f"[MIGRATION] Skipped {skipped_count} duplicate entries")
            
    except Exception as e:
        print(f"[MIGRATION] Error during migration: {e}")
        server_db.rollback()
    finally:
        server_db.close()
    
    print("[MIGRATION] Migration complete!")


if __name__ == "__main__":
    migrate_vulnerability_records()
