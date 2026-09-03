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


def text(driver: webdriver.Chrome, element_id: str) -> str:
    return driver.find_element(By.ID, element_id).text.strip()


def current_provenance(driver: webdriver.Chrome) -> dict[str, str]:
    return {
        "provider": text(driver, "retrieval-embedding-provider"),
        "model": text(driver, "retrieval-embedding-model"),
        "dimensions": text(driver, "retrieval-embedding-dimensions"),
    }


def fetch_evidence(driver: webdriver.Chrome, run_id: str) -> dict[str, object]:
    persisted = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        fetch(`/api/agents/runs/${arguments[0]}/evidence`)
          .then(response => response.json()).then(done)
          .catch(error => done({__error: String(error)}));
        """,
        run_id,
    )
    if persisted.get("__error"):
        raise AssertionError(persisted["__error"])
    return persisted


def expected_provenance(persisted: dict[str, object]) -> tuple[dict[str, str], dict[str, object]]:
    events = persisted.get("events") or []
    retrieved = next((event for event in reversed(events) if event.get("event_type") == "RAG_RETRIEVED"), None)
    if not retrieved:
        raise AssertionError("persisted RAG_RETRIEVED event missing")
    payload = retrieved.get("payload") or {}
    expected = {
        "provider": str(payload.get("embedding_provider")),
        "model": str(payload.get("embedding_model")),
        "dimensions": str(payload.get("embedding_dimensions")),
    }
    return expected, payload


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
        if text(driver, "retrieval-provenance-status") != "Retrieval provenance unavailable.":
            raise AssertionError("initial retrieval provenance must be unavailable")
        evidence["checks"].append("initial_unavailable")

        driver.find_element(By.ID, "run-button").click()
        wait.until(lambda d: text(d, "run-id") != "")
        first_run_id = text(driver, "run-id")
        wait.until(lambda d: text(d, "retrieval-provenance-status") == "Persisted current-run retrieval provenance.")

        first_persisted = fetch_evidence(driver, first_run_id)
        first_expected, first_payload = expected_provenance(first_persisted)
        first_actual = current_provenance(driver)
        if first_actual != first_expected:
            raise AssertionError(
                f"rendered provenance does not match persisted RAG_RETRIEVED payload: {first_actual!r} != {first_expected!r}"
            )
        evidence["checks"].append("persisted_provenance_rendered_exactly")

        # Stall only the next evidence request, then use the real Run button. renderRun() must
        # clear the previous run's provenance synchronously before the new evidence arrives.
        driver.execute_script(
            """
            window.__p024OriginalFetch = window.fetch;
            window.fetch = function(resource, init) {
              const url = String(resource);
              if (url.includes('/evidence')) {
                return new Promise(() => {});
              }
              return window.__p024OriginalFetch(resource, init);
            };
            """
        )
        driver.find_element(By.ID, "run-button").click()
        wait.until(lambda d: text(d, "run-id") not in ("", first_run_id))
        second_run_id = text(driver, "run-id")
        wait.until(lambda d: text(d, "retrieval-provenance-status") == "Retrieval provenance unavailable.")
        cleared = current_provenance(driver)
        unavailable = {"provider": "Unavailable", "model": "Unavailable", "dimensions": "Unavailable"}
        if cleared != unavailable:
            raise AssertionError(f"stale provenance remained after current-run change: {cleared!r}")
        evidence["checks"].append("run_change_clears_stale_provenance_before_evidence_arrives")

        # Restore real network behavior and exercise the visible refresh control to prove the
        # new current run can populate its own persisted provenance after the clear.
        driver.execute_script(
            """
            if (window.__p024OriginalFetch) {
              window.fetch = window.__p024OriginalFetch;
              delete window.__p024OriginalFetch;
            }
            """
        )
        driver.find_element(By.ID, "refresh-run-evidence-button").click()
        wait.until(lambda d: text(d, "retrieval-provenance-status") == "Persisted current-run retrieval provenance.")
        second_persisted = fetch_evidence(driver, second_run_id)
        second_expected, second_payload = expected_provenance(second_persisted)
        second_actual = current_provenance(driver)
        if second_actual != second_expected:
            raise AssertionError(
                f"refreshed provenance does not match second persisted run: {second_actual!r} != {second_expected!r}"
            )
        evidence["checks"].append("visible_refresh_rehydrates_current_run_provenance_exactly")

        evidence["first_run_id"] = first_run_id
        evidence["first_persisted_payload"] = first_payload
        evidence["first_rendered"] = first_actual
        evidence["second_run_id"] = second_run_id
        evidence["second_persisted_payload"] = second_payload
        evidence["second_rendered"] = second_actual
        evidence["cleared_between_runs"] = cleared

        screenshot = ARTIFACT_DIR / "operator-retrieval-provenance.png"
        driver.save_screenshot(str(screenshot))
        evidence["screenshot"] = str(screenshot)
        path = ARTIFACT_DIR / "operator-retrieval-provenance-evidence.json"
        path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(evidence, ensure_ascii=False))
    except Exception as error:
        evidence["failure"] = {"type": type(error).__name__, "message": str(error)}
        try:
            driver.save_screenshot(str(ARTIFACT_DIR / "operator-retrieval-provenance.png"))
        except Exception:
            pass
        (ARTIFACT_DIR / "operator-retrieval-provenance-evidence.json").write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
