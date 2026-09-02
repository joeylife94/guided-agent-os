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
RATIONALE_A = "Run A requires separate customer confirmation."
RATIONALE_B = "Run B is rejected for missing operator evidence."


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
        rationale_input = wait.until(EC.visibility_of_element_located((By.ID, "rejection-reason")))
        run_a = driver.find_element(By.ID, "run-id").text.strip()
        rationale_input.send_keys(RATIONALE_A)
        if rationale_input.get_attribute("value") != RATIONALE_A:
            raise AssertionError("Run A rationale was not entered as expected")
        evidence["run_a"] = run_a
        evidence["checks"].append("run_a_rationale_entered")

        driver.find_element(By.ID, "run-button").click()
        wait.until(lambda d: d.find_element(By.ID, "run-id").text.strip() not in ("", run_a))
        wait_text(wait, "run-status", "pending_approval")
        run_b = driver.find_element(By.ID, "run-id").text.strip()
        rationale_input = wait.until(EC.visibility_of_element_located((By.ID, "rejection-reason")))
        if rationale_input.get_attribute("value") != "":
            raise AssertionError(
                f"Run A rationale leaked into run B: {rationale_input.get_attribute('value')!r}"
            )
        evidence["run_b"] = run_b
        evidence["checks"].append("rationale_cleared_on_run_context_change")

        rationale_input.send_keys(f"  {RATIONALE_B}  ")
        driver.find_element(By.ID, "reject-button").click()
        wait_text(wait, "run-status", "rejected")

        persisted = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            Promise.all([
              fetch(`/api/agents/runs/${arguments[0]}`).then(response => response.json()),
              fetch(`/api/agents/runs/${arguments[0]}/events`).then(response => response.json()),
              fetch(`/api/agents/runs/${arguments[1]}`).then(response => response.json()),
              fetch(`/api/agents/runs/${arguments[1]}/events`).then(response => response.json()),
            ])
              .then(([runB, eventsB, runA, eventsA]) => done({runB, eventsB, runA, eventsA}))
              .catch(error => done({__error: String(error)}));
            """,
            run_b,
            run_a,
        )
        if persisted.get("__error"):
            raise AssertionError(persisted["__error"])

        run_b_data = persisted.get("runB") or {}
        events_b = persisted.get("eventsB") or []
        run_a_data = persisted.get("runA") or {}
        events_a = persisted.get("eventsA") or []
        types_b = [event.get("event_type") for event in events_b]
        types_a = [event.get("event_type") for event in events_a]
        rejected_b = next((event for event in events_b if event.get("event_type") == "REJECTED"), None)

        if run_b_data.get("status") != "rejected":
            raise AssertionError(f"Run B status is not rejected: {run_b_data!r}")
        if not rejected_b:
            raise AssertionError(f"Run B REJECTED audit event missing: {types_b!r}")
        if (rejected_b.get("payload") or {}).get("reason") != RATIONALE_B:
            raise AssertionError(f"Run B rejection rationale mismatch: {rejected_b!r}")
        if RATIONALE_A in json.dumps(rejected_b, ensure_ascii=False):
            raise AssertionError("Run A rationale was misattributed to run B rejection evidence")
        if "TOOL_EXECUTED" in types_b:
            raise AssertionError(f"Rejected run B emitted TOOL_EXECUTED: {types_b!r}")
        if run_a_data.get("status") != "pending_approval":
            raise AssertionError(f"Run A should remain pending_approval: {run_a_data!r}")
        if "REJECTED" in types_a or "TOOL_EXECUTED" in types_a:
            raise AssertionError(f"Run A was mutated while switching context: {types_a!r}")

        evidence["checks"].extend(
            [
                "run_b_specific_rationale_persisted",
                "run_a_rationale_not_misattributed",
                "run_b_rejected_without_tool_execution",
                "run_a_remains_pending_without_decision_mutation",
            ]
        )
        evidence["run_a_status"] = run_a_data.get("status")
        evidence["run_b_status"] = run_b_data.get("status")
        evidence["run_a_audit_types"] = types_a
        evidence["run_b_audit_types"] = types_b
        evidence["run_b_rejected_payload"] = rejected_b.get("payload") or {}

        screenshot_path = ARTIFACT_DIR / "operator-rejection-rationale-run-binding.png"
        driver.save_screenshot(str(screenshot_path))
        evidence["screenshot"] = str(screenshot_path)
        evidence_path = ARTIFACT_DIR / "operator-rejection-rationale-run-binding-evidence.json"
        evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(evidence, ensure_ascii=False))
    except Exception as error:
        evidence["failure"] = {"type": type(error).__name__, "message": str(error)}
        try:
            driver.save_screenshot(str(ARTIFACT_DIR / "operator-rejection-rationale-run-binding.png"))
        except Exception:
            pass
        (ARTIFACT_DIR / "operator-rejection-rationale-run-binding-evidence.json").write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
