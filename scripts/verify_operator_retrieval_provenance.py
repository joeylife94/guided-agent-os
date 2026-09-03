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
        run_id = text(driver, "run-id")
        wait.until(lambda d: text(d, "retrieval-provenance-status") == "Persisted current-run retrieval provenance.")

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
        actual = {
            "provider": text(driver, "retrieval-embedding-provider"),
            "model": text(driver, "retrieval-embedding-model"),
            "dimensions": text(driver, "retrieval-embedding-dimensions"),
        }
        if actual != expected:
            raise AssertionError(f"rendered provenance does not match persisted RAG_RETRIEVED payload: {actual!r} != {expected!r}")
        evidence["checks"].append("persisted_provenance_rendered_exactly")

        driver.execute_script("clearCurrentEvidence('P-024 browser proof clear')")
        wait.until(lambda d: text(d, "retrieval-provenance-status") == "Retrieval provenance unavailable.")
        cleared = {
            "provider": text(driver, "retrieval-embedding-provider"),
            "model": text(driver, "retrieval-embedding-model"),
            "dimensions": text(driver, "retrieval-embedding-dimensions"),
        }
        if cleared != {"provider": "Unavailable", "model": "Unavailable", "dimensions": "Unavailable"}:
            raise AssertionError(f"stale provenance remained after evidence clear: {cleared!r}")
        evidence["checks"].append("clear_removes_stale_provenance")
        evidence["run_id"] = run_id
        evidence["persisted_payload"] = payload
        evidence["rendered"] = actual

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
