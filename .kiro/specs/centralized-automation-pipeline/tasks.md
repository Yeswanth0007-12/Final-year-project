# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - Automation Pipeline Defects
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the 7 defects exist
  - **Scoped PBT Approach**: Test each defect condition separately to ensure reproducibility
  - Test implementation details from Fault Condition in design:
    - Schema inconsistency: Query both vulnerabilities table and VulnerabilityRecord table after scan, assert status values match
    - Queue instability: Spawn 10 threads calling add_to_patch_queue() simultaneously, verify queue integrity
    - Log clearing: Append 100 logs rapidly, verify all logs retained without clearing
    - No frontend updates: Update vulnerability status, poll dashboard endpoint, verify immediate reflection
    - Manual intervention required: Confirm automation, verify pipeline completes without manual steps
    - Inconsistent deduplication: Scan same vulnerability twice, verify only one entry exists
    - Pipeline termination on error: Inject validation failure for one vulnerability, verify pipeline continues
  - The test assertions should match the Expected Behavior Properties from design (unified schema, thread-safe queue, incremental logs, state notifications, full automation, consistent deduplication, error recovery)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bugs exist)
  - Document counterexamples found to understand root causes
  - Mark task complete when test is written, run, and failures are documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - API Compatibility and Core Logic
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs:
    - API endpoints return responses in expected format
    - Re-detection logic creates new entries for FIXED vulnerabilities on rescan
    - Patch generation using get_remediation_info() produces type-specific patches
    - Validation logic using validate_patch_logic() detects unsafe patterns
    - Scan sessions table maintains historical tracking fields
    - Frontend tab navigation works without page refresh
    - Background tasks execute asynchronously without blocking
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 3. Fix for centralized automation pipeline defects

  - [x] 3.1 Implement unified database schema
    - Deprecate VulnerabilityRecord table in scan_engine/intel/models.py
    - Migrate all scan engine modules to use vulnerabilities table from server.py
    - Standardize status enum: DETECTED, QUEUED_FOR_PATCH, PATCH_GENERATING, PATCH_APPLIED, VALIDATING, FIXED, FAILED
    - Update all queries in scan_engine/ modules to reference unified table
    - Create database migration script to merge existing VulnerabilityRecord entries
    - _Bug_Condition: input.vulnerabilityTable.status != input.vulnerabilityRecord.status (schema inconsistency)_
    - _Expected_Behavior: Single unified schema with consistent status values across all modules_
    - _Preservation: API endpoint contracts must return responses in same format (3.1)_
    - _Requirements: 1.1, 2.1, 3.1_

  - [x] 3.2 Implement thread-safe queue processing
    - Replace global patch_queue list with queue.Queue() from threading module
    - Replace global active_patch variable with queue state tracking
    - Replace global pipeline_paused with threading.Event() for proper signaling
    - Implement single dedicated worker thread that processes queue items sequentially
    - Add proper locking mechanisms for queue operations
    - _Bug_Condition: input.queueOperation == 'add_to_patch_queue' AND input.concurrentAccess == true AND input.threadSafety == false_
    - _Expected_Behavior: Thread-safe FIFO queue with proper synchronization_
    - _Preservation: Background task execution using FastAPI BackgroundTasks or threading.Thread must remain unchanged (3.7)_
    - _Requirements: 1.2, 2.2, 3.7_

  - [x] 3.3 Implement incremental log streaming
    - Modify append_log() to ensure it only appends to existing log arrays, never replaces dictionary
    - Add index tracking fields last_index_scanner and last_index_automation to terminal_sessions
    - Update /terminal-stream endpoint to return only new logs since last_index
    - Implement proper initialization check to prevent dictionary replacement
    - _Bug_Condition: input.logStreamOperation == 'append_log' AND input.terminalSessions[sessionId] IS REPLACED_
    - _Expected_Behavior: Logs append incrementally without clearing, with proper index tracking_
    - _Preservation: API endpoint /terminal-stream must return responses in same format (3.1)_
    - _Requirements: 1.3, 2.3, 3.1_

  - [x] 3.4 Implement state change notifications
    - Enhance trigger_pipeline_update() to set global flag or event when state changes
    - Modify frontend polling logic to check for state change flag
    - Add timestamp tracking to detect when database updates occur
    - Implement polling optimization to reduce unnecessary requests
    - _Bug_Condition: input.databaseStateChanged == true AND input.frontendNotificationSent == false_
    - _Expected_Behavior: Frontend updates automatically when database state changes_
    - _Preservation: Frontend tab navigation without page refresh must continue working (3.6)_
    - _Requirements: 1.4, 2.4, 3.6_

  - [x] 3.5 Implement centralized pipeline orchestrator
    - Create new PipelineManager class that manages complete automation flow
    - Implement state machine with transitions: SCAN → DETECT → QUEUE → GENERATE → VALIDATE → FIXED/FAILED
    - Add orchestration logic in confirm_automation() endpoint to trigger PipelineManager
    - Add progress tracking and status reporting
    - _Bug_Condition: input.executiveScanConfirmed == true AND input.manualStepsRequired > 0_
    - _Expected_Behavior: Entire pipeline runs automatically without manual intervention_
    - _Preservation: Re-detection logic for FIXED vulnerabilities must continue creating new entries (3.2)_
    - _Requirements: 1.5, 2.5, 3.2_

  - [x] 3.6 Implement consistent deduplication
    - Standardize deduplication key to (website_name, line_number, vulnerability_type) across all modules
    - Update scan_engine deduplication logic to use same key format
    - Remove MD5 hash-based deduplication from scan engine
    - Add deduplication validation in database constraints
    - _Bug_Condition: input.serverDeduplicationKey != input.scanEngineDeduplicationKey_
    - _Expected_Behavior: Consistent deduplication key prevents duplicates across all modules_
    - _Preservation: Scan session tracking in scan_sessions table must remain unchanged (3.5)_
    - _Requirements: 1.6, 2.6, 3.5_

  - [x] 3.7 Implement per-vulnerability error handling
    - Modify run_patch_pipeline() to wrap individual vulnerability processing in try-except
    - On exception, mark vulnerability status as FAILED and log error details
    - Continue processing next item in queue instead of terminating worker thread
    - Add error categorization for better debugging
    - _Bug_Condition: input.patchValidationFailed == true AND input.pipelineContinues == false_
    - _Expected_Behavior: Pipeline continues processing remaining vulnerabilities when individual items fail_
    - _Preservation: Patch generation using get_remediation_info() must remain unchanged (3.3), Validation logic using validate_patch_logic() must remain unchanged (3.4)_
    - _Requirements: 1.7, 2.7, 3.3, 3.4_

  - [x] 3.8 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Unified Schema and Full Automation
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 3.9 Verify preservation tests still pass
    - **Property 2: Preservation** - API Compatibility and Core Logic
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
