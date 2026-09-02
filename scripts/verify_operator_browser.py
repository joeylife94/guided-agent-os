from __future__ import annotations

import json
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = os.getenv("OPERATOR_BASE_URL", "http://127.0.0.1:18701")
ARTIFACT_DIR = Path(os.getenv("OPERATOR_ARTIFACT_DIR", "/tmp"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def wait_text(wait: WebDriverWait, element_id: str, expected: str) -> None:
    wait.until(lambda driver: expected in driver.find_element(By.ID, element_id).text)


def audit_types(driver: webdriver.Chrome) -> list[str]:
    return [element.text for element in driver.find_elements(By.CSS_SELECTOR, "#audit-timeline .audit-type")]


def wait_audit_sequence(wait: WebDriverWait, expected: list[str]) -> list[str]:
    def _matches(driver: webdriver.Chrome) -> list[str] | bool:
        types = audit_types(driver)
        positions = [types.index(item) for item in expected if item in types]
        if len(positions) == len(expected) and positions == sorted(positions):
            return types
        return False

    return wait.until(_matches)


def main() -> None:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1400")

    evidence: dict[str, object] = {"base_url": BASE_URL, "checks": []}
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(BASE_URL)
        wait.until(EC.visibility_of_element_located((By.ID, "agent-form")))
        evidence["checks"].append("workspace_loaded")

        business_context = driver.find_element(By.ID, "business_context")
        business_context.clear()
        driver.find_element(By.ID, "run-button").click()

        wait_text(wait, "run-status", "needs_clarification")
        wait.until(EC.visibility_of_element_located((By.ID, "clarification-panel")))
        clarification_text = driver.find_element(By.ID, "clarification-questions").text
        if "What is the business context" not in clarification_text:
            raise AssertionError(f"Expected business-context clarification, got: {clarification_text!r}")
        clarification_audit = wait_audit_sequence(wait, ["REQUEST_RECEIVED", "CLARIFICATION_REQUIRED"])
        evidence["checks"].append("clarification_rendered")
        evidence["checks"].append("clarification_audit_timeline_rendered")
        evidence["clarification"] = clarification_text
        evidence["clarification_audit_types"] = clarification_audit

        business_context.send_keys(
            "Internal maintenance operator needs a controlled lookup before reviewing a historical facility record."
        )
        driver.find_element(By.ID, "run-button").click()

        wait_text(wait, "run-status", "pending_approval")
        wait.until(EC.visibility_of_element_located((By.ID, "review-panel")))
        wait.until(EC.visibility_of_element_located((By.ID, "execution-input-review")))
        pending_audit = wait_audit_sequence(
            wait,
            [
                "REQUEST_RECEIVED",
                "VALIDATION_PASSED",
                "NORMALIZED",
                "RAG_RETRIEVED",
                "ANSWER_GENERATED",
                "TOOL_PLANNED",
                "APPROVAL_REQUESTED",
            ],
        )
        evidence["checks"].append("pending_approval_rendered")
        evidence["checks"].append("pending_audit_timeline_rendered")
        evidence["pending_run_id"] = driver.find_element(By.ID, "run-id").text
        evidence["pending_audit_types"] = pending_audit

        pending_run_id = str(evidence["pending_run_id"])
        pending_persisted = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch(`/api/agents/runs/${arguments[0]}`)
              .then(response => response.json())
              .then(run => done({run}))
              .catch(error => done({__error: String(error)}));
            """,
            pending_run_id,
        )
        if pending_persisted.get("__error"):
            raise AssertionError(pending_persisted["__error"])
        pending_run = pending_persisted.get("run") or {}
        pending_intake = pending_run.get("intake_data") or {}
        pending_tool_plan = pending_run.get("tool_plan") or {}
        recommended = pending_tool_plan.get("recommended_tools") or []
        expected_tool = (
            (recommended[0] or {}).get("name") if recommended else None
        ) or pending_tool_plan.get("tool_name") or pending_tool_plan.get("tool") or "Not available."
        expected_parameters = pending_intake.get("tool_parameters")
        expected_allowed_tools = pending_intake.get("allowed_tools")

        rendered_tool = driver.find_element(By.ID, "execution-planned-tool").text
        rendered_parameters = driver.find_element(By.ID, "execution-tool-parameters").text
        rendered_allowed_tools = driver.find_element(By.ID, "execution-allowed-tools").text
        if rendered_tool != expected_tool:
            raise AssertionError(
                f"Approval planned tool differs from persisted run: rendered={rendered_tool!r} persisted={expected_tool!r}"
            )
        if json.loads(rendered_parameters) != expected_parameters:
            raise AssertionError(
                f"Approval tool parameters differ from persisted run: rendered={rendered_parameters!r} persisted={expected_parameters!r}"
            )
        if json.loads(rendered_allowed_tools) != expected_allowed_tools:
            raise AssertionError(
                f"Approval allowed tools differ from persisted run: rendered={rendered_allowed_tools!r} persisted={expected_allowed_tools!r}"
            )
        evidence["checks"].append("approval_execution_inputs_match_persisted_run")
        evidence["approval_execution_inputs"] = {
            "planned_tool": rendered_tool,
            "tool_parameters": json.loads(rendered_parameters),
            "allowed_tools": json.loads(rendered_allowed_tools),
        }

        wait.until(
            lambda d: len(d.find_element(By.ID, "execution-inputs-digest").text.strip()) == 64
        )
        wait.until(lambda d: d.find_element(By.ID, "approve-button").is_enabled())
        reviewed_digest = driver.find_element(By.ID, "execution-inputs-digest").text.strip()
        evidence["checks"].append("reviewed_execution_inputs_digest_ready")
        evidence["reviewed_execution_inputs_digest"] = reviewed_digest

        stale_digest = "0" * 64
        if stale_digest == reviewed_digest:
            stale_digest = "f" * 64
        rejected = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch(`/api/agents/runs/${arguments[0]}/approve`, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                note: 'Intentional stale digest for browser proof.',
                expected_execution_inputs_digest: arguments[1],
              }),
            })
              .then(async response => done({status: response.status, body: await response.json()}))
              .catch(error => done({__error: String(error)}));
            """,
            pending_run_id,
            stale_digest,
        )
        if rejected.get("__error"):
            raise AssertionError(rejected["__error"])
        if rejected.get("status") != 409:
            raise AssertionError(f"Expected stale approval digest to return 409, got: {rejected!r}")

        rejected_state_result = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch(`/api/agents/runs/${arguments[0]}`)
              .then(response => response.json())
              .then(run => done({run}))
              .catch(error => done({__error: String(error)}));
            """,
            pending_run_id,
        )
        if rejected_state_result.get("__error"):
            raise AssertionError(rejected_state_result["__error"])
        rejected_run = rejected_state_result.get("run") or {}
        if rejected_run.get("status") != "pending_approval":
            raise AssertionError(f"Expected rejected approval to remain pending_approval, got: {rejected_run!r}")

        wait.until(lambda d: d.find_element(By.ID, "refresh-run-evidence-button").is_enabled())
        driver.find_element(By.ID, "refresh-run-evidence-button").click()
        wait.until(EC.visibility_of_element_located((By.ID, "approval-precondition-rejection")))
        wait_text(wait, "approval-precondition-rejection-message", "digest_mismatch")
        submitted_digest = driver.find_element(By.ID, "approval-rejection-submitted-digest").text.strip()
        current_digest = driver.find_element(By.ID, "approval-rejection-current-digest").text.strip()
        if submitted_digest != stale_digest:
            raise AssertionError(
                f"Operator submitted rejection digest differs from attempted digest: rendered={submitted_digest!r} attempted={stale_digest!r}"
            )
        if current_digest != reviewed_digest:
            raise AssertionError(
                f"Operator current rejection digest differs from reviewed digest: rendered={current_digest!r} reviewed={reviewed_digest!r}"
            )

        rejected_events_result = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch(`/api/agents/runs/${arguments[0]}/events`)
              .then(response => response.json())
              .then(events => done({events}))
              .catch(error => done({__error: String(error)}));
            """,
            pending_run_id,
        )
        if rejected_events_result.get("__error"):
            raise AssertionError(rejected_events_result["__error"])
        rejected_events = rejected_events_result.get("events") or []
        rejected_types = [event.get("event_type") for event in rejected_events]
        if "APPROVAL_PRECONDITION_REJECTED" not in rejected_types:
            raise AssertionError(f"Persisted rejection event missing: {rejected_types!r}")
        if "APPROVED" in rejected_types or "TOOL_EXECUTED" in rejected_types:
            raise AssertionError(f"Rejected attempt emitted false execution evidence: {rejected_types!r}")
        evidence["checks"].append("stale_digest_rejected_409_pending_approval")
        evidence["checks"].append("rejection_notice_renders_submitted_and_current_digests")
        evidence["checks"].append("rejected_attempt_has_no_false_execution_events")
        evidence["rejected_approval"] = {
            "submitted_digest": submitted_digest,
            "current_digest": current_digest,
            "audit_types": rejected_types,
        }

        driver.find_element(By.ID, "approve-button").click()
        wait_text(wait, "run-status", "archived")
        wait.until(lambda d: '\"status\": \"executed\"' in d.find_element(By.ID, "execution-result").text)

        execution_text = driver.find_element(By.ID, "execution-result").text
        if '\"tool_name\": \"legacy_db_lookup\"' not in execution_text:
            raise AssertionError(f"Expected legacy_db_lookup execution result, got: {execution_text!r}")
        if '\"record_id\": \"LEG-001\"' not in execution_text:
            raise AssertionError(f"Expected LEG-001 execution result, got: {execution_text!r}")

        final_audit = wait_audit_sequence(wait, ["RAG_RETRIEVED", "APPROVED", "TOOL_EXECUTED", "COMPLETED"])
        evidence["checks"].append("approved_execution_rendered")
        evidence["checks"].append("persisted_audit_timeline_rendered")
        evidence["execution_result"] = json.loads(execution_text)
        evidence["final_status"] = driver.find_element(By.ID, "run-status").text
        evidence["final_run_id"] = driver.find_element(By.ID, "run-id").text
        evidence["final_audit_types"] = final_audit

        run_id = str(evidence["final_run_id"])
        persisted = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            Promise.all([
              fetch(`/api/agents/runs/${arguments[0]}`).then(response => response.json()),
              fetch(`/api/agents/runs/${arguments[0]}/events`).then(response => response.json()),
            ])
              .then(([run, events]) => done({run, events}))
              .catch(error => done({__error: String(error)}));
            """,
            run_id,
        )
        if persisted.get("__error"):
            raise AssertionError(persisted["__error"])
        persisted_run = persisted.get("run") or {}
        persisted_events = persisted.get("events") or []
        persisted_execution = (persisted_run.get("raw_output") or {}).get("execution_result")
        if not persisted_execution or persisted_execution.get("status") != "executed":
            raise AssertionError(f"Persisted execution result missing: {persisted_run!r}")

        persisted_types = [event.get("event_type") for event in persisted_events]
        if persisted_types != final_audit:
            raise AssertionError(
                f"Rendered audit timeline differs from persisted events: rendered={final_audit!r} persisted={persisted_types!r}"
            )
        required_tail = ["RAG_RETRIEVED", "APPROVED", "TOOL_EXECUTED", "COMPLETED"]
        required_positions = [persisted_types.index(item) for item in required_tail]
        if required_positions != sorted(required_positions):
            raise AssertionError(f"Required audit events out of order: {persisted_types!r}")

        approved_event = next(event for event in persisted_events if event.get("event_type") == "APPROVED")
        executed_event = next(event for event in persisted_events if event.get("event_type") == "TOOL_EXECUTED")
        approved_digest = (approved_event.get("payload") or {}).get("execution_inputs_digest")
        executed_digest = (executed_event.get("payload") or {}).get("execution_inputs_digest")
        if approved_digest != reviewed_digest or executed_digest != reviewed_digest:
            raise AssertionError(
                "Reviewed browser digest must match persisted APPROVED and TOOL_EXECUTED correlation: "
                f"reviewed={reviewed_digest!r} approved={approved_digest!r} executed={executed_digest!r}"
            )

        evidence["checks"].append("persisted_execution_reloaded")
        evidence["checks"].append("persisted_audit_reloaded_and_matches_ui")
        evidence["checks"].append("reviewed_digest_matches_persisted_approval_execution_correlation")
        evidence["persisted_status"] = persisted_run.get("status")
        evidence["persisted_audit_types"] = persisted_types

        screenshot_path = ARTIFACT_DIR / "operator-golden-path.png"
        driver.save_screenshot(str(screenshot_path))
        evidence["screenshot"] = str(screenshot_path)

        evidence_path = ARTIFACT_DIR / "operator-browser-evidence.json"
        evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(evidence, ensure_ascii=False))
    except Exception as error:
        evidence["failure"] = {"type": type(error).__name__, "message": str(error)}
        try:
            evidence["failure_run_id"] = driver.find_element(By.ID, "run-id").text
            evidence["failure_run_status"] = driver.find_element(By.ID, "run-status").text
            evidence["failure_rejection_visible"] = driver.find_element(By.ID, "approval-precondition-rejection").is_displayed()
            evidence["failure_rejection_message"] = driver.find_element(By.ID, "approval-precondition-rejection-message").text
            evidence["failure_evidence_json"] = driver.find_element(By.ID, "run-evidence-json").text
            driver.save_screenshot(str(ARTIFACT_DIR / "operator-golden-path.png"))
        except Exception as diagnostic_error:
            evidence["diagnostic_error"] = str(diagnostic_error)
        (ARTIFACT_DIR / "operator-browser-evidence.json").write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
