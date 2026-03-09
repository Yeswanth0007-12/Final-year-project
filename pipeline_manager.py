"""
Centralized Pipeline Manager
Orchestrates the complete automation flow: SCAN → DETECT → QUEUE → GENERATE → VALIDATE → FIXED/FAILED
"""
import threading
import time
from typing import List
from server import SessionLocal, Vulnerability, trigger_pipeline_update, append_log


class PipelineManager:
    """
    Centralized orchestrator for the vulnerability remediation pipeline.
    Manages state transitions and coordinates all pipeline phases.
    """
    
    def __init__(self):
        self.state_machine = {
            "DETECTED": "QUEUED_FOR_PATCH",
            "QUEUED_FOR_PATCH": "PATCH_GENERATING",
            "PATCH_GENERATING": "PATCH_APPLIED",
            "PATCH_APPLIED": "VALIDATING",
            "VALIDATING": ["FIXED", "FAILED"]  # Terminal states
        }
    
    def transition_state(self, vuln_id: str, from_state: str, to_state: str) -> bool:
        """
        Transition a vulnerability from one state to another.
        Returns True if transition successful, False otherwise.
        """
        db = SessionLocal()
        try:
            vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
            if not vuln:
                return False
            
            # Validate transition
            expected_next = self.state_machine.get(from_state)
            if expected_next:
                if isinstance(expected_next, list):
                    if to_state not in expected_next:
                        return False
                elif to_state != expected_next:
                    return False
            
            # Perform transition
            vuln.status = to_state
            db.commit()
            trigger_pipeline_update()
            return True
            
        except Exception as e:
            print(f"[PIPELINE_MANAGER] Error transitioning {vuln_id}: {e}")
            return False
        finally:
            db.close()
    
    def get_pipeline_progress(self) -> dict:
        """
        Get current pipeline progress statistics.
        """
        db = SessionLocal()
        try:
            stats = {
                "DETECTED": db.query(Vulnerability).filter(Vulnerability.status == "DETECTED").count(),
                "QUEUED_FOR_PATCH": db.query(Vulnerability).filter(Vulnerability.status == "QUEUED_FOR_PATCH").count(),
                "PATCH_GENERATING": db.query(Vulnerability).filter(Vulnerability.status == "PATCH_GENERATING").count(),
                "PATCH_APPLIED": db.query(Vulnerability).filter(Vulnerability.status == "PATCH_APPLIED").count(),
                "VALIDATING": db.query(Vulnerability).filter(Vulnerability.status == "VALIDATING").count(),
                "FIXED": db.query(Vulnerability).filter(Vulnerability.status == "FIXED").count(),
                "FAILED": db.query(Vulnerability).filter(Vulnerability.status == "FAILED").count()
            }
            return stats
        finally:
            db.close()
    
    def get_vulnerabilities_by_status(self, status: str) -> List[Vulnerability]:
        """
        Get all vulnerabilities with a specific status.
        """
        db = SessionLocal()
        try:
            return db.query(Vulnerability).filter(Vulnerability.status == status).all()
        finally:
            db.close()
    
    def orchestrate_full_pipeline(self, scan_id: str, vuln_ids: List[str]):
        """
        Orchestrate the complete pipeline for a list of vulnerabilities.
        This is called after executive scan confirmation.
        """
        append_log(scan_id, f"[PIPELINE_MANAGER] Orchestrating pipeline for {len(vuln_ids)} vulnerabilities", log_type="automation")
        
        # All vulnerabilities start as DETECTED
        # They will be transitioned through the pipeline by the patch queue worker
        # This method just logs the orchestration start
        
        append_log(scan_id, "[PIPELINE_MANAGER] Pipeline orchestration initiated", log_type="automation")


# Global pipeline manager instance
pipeline_manager = PipelineManager()
