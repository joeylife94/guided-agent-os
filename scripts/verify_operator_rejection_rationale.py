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
RATIONALE = "Missing required client confirmation."


def wait_text(wait: WebDriverWait, element_id: str, expected: str) -> None:
    wait.until(lambda driver: expected in driver.find_element(By.ID, element_id).text)


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
        driver.find_element(By.ID, "run-button").click()
        wait_text(wait, "run-status", "pending_approval")
        wait.until(EC.visibility_of_element_located((By.ID, "review-panel")))
        rationale_input = wait.until(EC.visibility_of_element_located((By.ID, "rejection-reason")))
        run_id = driver.find_element(By.ID, "run-id").text.strip()
        evidence["run_id"] = run_id
        evidence["checks"].append("pending_approval_with_rationale_input")

        driver.find_element(By.ID, "reject-button").click()
        wait_text(wait, "request-error", "Rejection rationale is required.")
        if "pending_approval" not in driver.find_element(By.ID, "run-status").text:
            raise AssertionError("Blank rationale must not leave pending_approval")
        evidence["checks"].append("blank_rationale_blocked_client_side")

        rationale_input.send_keys(f"  {RATIONALE}  ")
        driver.find_element(By.ID, "reject-button").click()
        wait_text(wait, "run-status", "rejected")

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

        run = persisted.get("run") or {}
        events = persisted.get("events") or []
        types = [event.get("event_type") for event in events]
        rejected_event = next((event for event in events if event.get("event_type") == "REJECTED"), None)
        if run.get("status") != "rejected":
            raise AssertionError(f"Persisted run status is not rejected: {run!r}")
        if not rejected_event:
            raise AssertionError(f"Persisted REJECTED audit event missing: {types!r}")
        if (rejected_event.get("payload") or {}).get("reason") != RATIONALE:
            raise AssertionError(f"Persisted rejection rationale mismatch: {rejected_event!r}")
        if "TOOL_EXECUTED" in types:
            raise AssertionError(f"Rejected run emitted TOOL_EXECUTED: {types!r}")

        evidence["checks"].extend(
            [
                "trimmed_human_rationale_persisted_in_rejected_audit_event",
                "rejected_run_has_no_tool_execution",
            ]
        )
        evidence["persisted_status"] = run.get("status")
        evidence["audit_types"] = types
        evidence["rejected_payload"] = rejected_event.get("payload") or {}

        screenshot_path = ARTIFACT_DIR / "operator-rejection-rationale.png"
        driver.save_screenshot(str(screenshot_path))
        evidence["screenshot"] = str(screenshot_path)
        evidence_path = ARTIFACT_DIR / "operator-rejection-rationale-evidence.json"
        evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(evidence, ensure_ascii=False))
    except Exception as error:
        evidence["failure"] = {"type": type(error).__name__, "message": str(error)}
        try:
            driver.save_screenshot(str(ARTIFACT_DIR / "operator-rejection-rationale.png"))
        except Exception:
            pass
        (ARTIFACT_DIR / "operator-rejection-rationale-evidence.json").write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
