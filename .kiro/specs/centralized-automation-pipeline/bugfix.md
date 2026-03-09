# Bugfix Requirements Document

## Introduction

The DevSecOps vulnerability management application currently suffers from critical architectural issues preventing full automation. The system maintains two separate database schemas (server.py's `vulnerabilities` table and scan_engine's `VulnerabilityRecord` table) with incompatible status enums, lacks centralized pipeline orchestration, has unstable queue processing, and exhibits terminal log clearing behavior. These issues prevent the automated pipeline flow: SCAN → DETECT → QUEUE → GENERATE PATCHES → VALIDATE → UPDATE STATUS → UPDATE ALL MODULES.

This bugfix addresses the core synchronization and automation stability issues to enable a fully automated, hands-free vulnerability remediation pipeline after the user confirms the automation queue.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the system detects vulnerabilities during a scan THEN modules display inconsistent data because server.py uses `vulnerabilities` table with status values (DETECTED, QUEUED_FOR_PATCH, PATCH_GENERATING, PATCH_APPLIED, VALIDATING, FIXED, FAILED) while scan_engine uses `VulnerabilityRecord` table with different status enum (Detected, AI_Fix_Generated, Validated, Fixed, Rejected)

1.2 WHEN vulnerabilities are added to the patch queue THEN the queue processing is unstable because `process_patch_queue()` uses global variables (`active_patch`, `patch_queue`, `pipeline_paused`) without thread-safe synchronization and the queue can be corrupted by concurrent access

1.3 WHEN terminal logs are streamed to the frontend THEN logs clear or flicker instead of appending because the `terminal_sessions` dictionary is replaced rather than appended to, and the frontend polling mechanism doesn't properly track incremental log indices

1.4 WHEN a scan completes and patches are generated THEN the Dashboard and Vulnerabilities Tab do not update automatically because there is no event notification mechanism to trigger frontend refreshes after database state changes

1.5 WHEN the Executive Scan runs and user confirms automation THEN manual intervention is still required at multiple steps because the pipeline lacks a centralized orchestrator to manage state transitions and the `run_patch_pipeline()` function processes vulnerabilities sequentially without proper error recovery

1.6 WHEN vulnerabilities are deduplicated during scanning THEN duplicates still appear because server.py uses `(website_name, line_number, vulnerability_type)` as dedup key while scan_engine uses `md5(file_path:line_number:name)`, creating inconsistent deduplication logic

1.7 WHEN patch validation fails for a vulnerability THEN the pipeline does not continue processing remaining vulnerabilities because error handling in `run_patch_pipeline()` terminates the entire worker thread instead of marking the individual vulnerability as FAILED and continuing

### Expected Behavior (Correct)

2.1 WHEN the system detects vulnerabilities during a scan THEN all modules SHALL display consistent data by using a single unified `vulnerabilities` table with standardized status values (DETECTED → QUEUED_FOR_PATCH → PATCH_GENERATING → PATCH_APPLIED → VALIDATING → FIXED → FAILED)

2.2 WHEN vulnerabilities are added to the patch queue THEN the queue processing SHALL be stable using a thread-safe FIFO queue implementation with a single dedicated worker thread that processes one vulnerability at a time

2.3 WHEN terminal logs are streamed to the frontend THEN logs SHALL append incrementally without clearing by maintaining separate log arrays for scanner and automation logs, with proper index tracking for incremental polling

2.4 WHEN a scan completes and patches are generated THEN the Dashboard and Vulnerabilities Tab SHALL update automatically by implementing a state change notification mechanism that triggers frontend polling or WebSocket updates

2.5 WHEN the Executive Scan runs and user confirms automation THEN the entire pipeline SHALL run automatically without manual intervention by implementing a PipelineManager service that orchestrates all state transitions: SCAN → DETECT → QUEUE → GENERATE PATCHES → VALIDATE → UPDATE STATUS → UPDATE ALL MODULES

2.6 WHEN vulnerabilities are deduplicated during scanning THEN duplicates SHALL be prevented using a consistent deduplication key `(website_name, line_number, vulnerability_type)` across all scanning modules

2.7 WHEN patch validation fails for a vulnerability THEN the pipeline SHALL continue processing remaining vulnerabilities by catching exceptions per vulnerability, marking it as FAILED, logging the error, and proceeding to the next item in the queue

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the frontend makes API calls to existing endpoints (`/scan`, `/initialize-audit/{website_id}`, `/pipeline/start`, `/pipeline/status`, `/terminal-stream`, `/available-websites`, `/vulnerabilities`, `/dashboard-stats`) THEN the system SHALL CONTINUE TO return responses in the same format to maintain frontend compatibility

3.2 WHEN vulnerabilities are in FIXED status and a rescan detects the same vulnerability pattern with different code THEN the system SHALL CONTINUE TO create a new vulnerability entry (re-detection logic) as currently implemented

3.3 WHEN the patch generation logic creates remediation code for vulnerability types (EVAL_INJECTION, EXEC_INJECTION, SQL_INJECTION, DOM_XSS) THEN the system SHALL CONTINUE TO use the existing `get_remediation_info()` function with type-specific patch templates

3.4 WHEN the validation logic checks patched code THEN the system SHALL CONTINUE TO use the existing `validate_patch_logic()` function with regex-based unsafe pattern detection

3.5 WHEN scan sessions are created THEN the system SHALL CONTINUE TO maintain the `scan_sessions` table with fields (id, created_at, total_files_scanned, total_vulnerabilities, overall_risk_score) for historical tracking

3.6 WHEN the user navigates between frontend tabs (Dashboard, Vulnerabilities, Patch Lab, Decision Tree, System Core, Compliance, Feedback, Terminal, Website Scanner) THEN the system SHALL CONTINUE TO display the correct view without requiring page refresh

3.7 WHEN background tasks are executed for scanning or patching THEN the system SHALL CONTINUE TO use FastAPI's BackgroundTasks or threading.Thread for asynchronous processing without blocking the API response
