from __future__ import annotations

import json
import os
import time
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


def main() -> None:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1200")

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
        evidence["checks"].append("clarification_rendered")
        evidence["clarification"] = clarification_text

        business_context.send_keys(
            "Internal maintenance operator needs a controlled lookup before reviewing a historical facility record."
        )
        driver.find_element(By.ID, "run-button").click()

        wait_text(wait, "run-status", "pending_approval")
        wait.until(EC.visibility_of_element_located((By.ID, "review-panel")))
        evidence["checks"].append("pending_approval_rendered")
        evidence["pending_run_id"] = driver.find_element(By.ID, "run-id").text

        driver.find_element(By.ID, "approve-button").click()
        wait_text(wait, "run-status", "archived")
        wait.until(lambda d: '"status": "executed"' in d.find_element(By.ID, "execution-result").text)

        execution_text = driver.find_element(By.ID, "execution-result").text
        if '"tool_name": "legacy_db_lookup"' not in execution_text:
            raise AssertionError(f"Expected legacy_db_lookup execution result, got: {execution_text!r}")
        if '"record_id": "LEG-001"' not in execution_text:
            raise AssertionError(f"Expected LEG-001 execution result, got: {execution_text!r}")
        evidence["checks"].append("approved_execution_rendered")
        evidence["execution_result"] = json.loads(execution_text)
        evidence["final_status"] = driver.find_element(By.ID, "run-status").text
        evidence["final_run_id"] = driver.find_element(By.ID, "run-id").text

        # Persisted result check through a fresh page-side API read, proving the UI result
        # corresponds to backend-persisted run state rather than transient DOM-only state.
        run_id = str(evidence["final_run_id"])
        persisted = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch(`/api/agents/runs/${arguments[0]}`)
              .then(response => response.json())
              .then(payload => done(payload))
              .catch(error => done({__error: String(error)}));
            """,
            run_id,
        )
        if persisted.get("__error"):
            raise AssertionError(persisted["__error"])
        persisted_execution = (persisted.get("raw_output") or {}).get("execution_result")
        if not persisted_execution or persisted_execution.get("status") != "executed":
            raise AssertionError(f"Persisted execution result missing: {persisted!r}")
        evidence["checks"].append("persisted_execution_reloaded")
        evidence["persisted_status"] = persisted.get("status")

        screenshot_path = ARTIFACT_DIR / "operator-golden-path.png"
        driver.save_screenshot(str(screenshot_path))
        evidence["screenshot"] = str(screenshot_path)

        evidence_path = ARTIFACT_DIR / "operator-browser-evidence.json"
        evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(evidence, ensure_ascii=False))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
