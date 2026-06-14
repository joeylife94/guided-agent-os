"""
Tests for agent run persistence (Phase 2-A).

Verifies that:
- Validated runs are persisted to the database
- Needs_clarification runs are persisted to the database
- GET endpoint retrieves saved runs by run_id
- GET endpoint returns 404 for unknown run_id
"""

from __future__ import annotations

import unittest
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import after setup to ensure dependency overrides are in place
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create tables in test database
Base.metadata.create_all(bind=engine)

# Create test app
app_under_test = FastAPI(
    title="Guided Agent OS",
    description="A form-driven AI agent platform.",
    version="0.1.0",
)

app_under_test.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_under_test.include_router(router)
app_under_test.dependency_overrides[get_db] = override_get_db

client = TestClient(app_under_test)


class AgentRunPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set up test database before each test."""
        # Clear all existing data from all tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def tearDown(self) -> None:
        """Clean up test database after each test."""
        Base.metadata.drop_all(bind=engine)

    def _run_count(self) -> int:
        db = TestingSessionLocal()
        try:
            return db.query(AgentRun).count()
        finally:
            db.close()

    def test_validated_run_is_persisted(self) -> None:
        """Verify that a validated run is saved to the database."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "Early-stage fintech startup",
            "project_description": "Dashboard with MRR and churn charts",
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "validated")
        self.assertIsNotNone(data["run_id"])
        self.assertEqual(data["agent_type"], "freelance")
        self.assertEqual(data["intake_data"], intake_data)
        self.assertEqual(data["missing_fields"], [])
        self.assertEqual(data["clarification_questions"], [])
        self.assertEqual(self._run_count(), 1)

        # Verify the run was persisted to the database
        db = TestingSessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.id == data["run_id"]).first()
            self.assertIsNotNone(run, "Run should be persisted in database")
            self.assertEqual(run.status, "validated")
            self.assertEqual(run.agent_type, "freelance")
            self.assertEqual(run.intake_data, intake_data)
        finally:
            db.close()

    def test_needs_clarification_run_is_persisted(self) -> None:
        """Verify that a needs_clarification run is saved to the database."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            # Missing required fields: client_description, project_description
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "needs_clarification")
        self.assertIsNotNone(data["run_id"])
        self.assertEqual(data["agent_type"], "freelance")
        self.assertEqual(data["intake_data"], intake_data)
        self.assertIn("client_description", data["missing_fields"])
        self.assertIn("project_description", data["missing_fields"])
        self.assertGreater(len(data["clarification_questions"]), 0)
        self.assertEqual(self._run_count(), 1)

        # Verify the run was persisted to the database
        db = TestingSessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.id == data["run_id"]).first()
            self.assertIsNotNone(run, "Run should be persisted in database")
            self.assertEqual(run.status, "needs_clarification")
            self.assertEqual(run.agent_type, "freelance")
            self.assertEqual(run.intake_data, intake_data)
            # Verify missing fields were captured
            self.assertIn("client_description", run.missing_fields)
            self.assertIn("project_description", run.missing_fields)
            # Verify clarification questions were captured
            self.assertGreater(len(run.clarification_questions), 0)
        finally:
            db.close()

    def test_whitespace_only_required_field_persists_as_needs_clarification(self) -> None:
        """Verify whitespace-only required fields are persisted as missing."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "Early-stage fintech startup",
            "project_description": "   \t\n",
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "needs_clarification")
        self.assertEqual(data["missing_fields"], ["project_description"])
        self.assertEqual(data["intake_data"], intake_data)
        self.assertEqual(self._run_count(), 1)

        db = TestingSessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.id == data["run_id"]).first()
            self.assertIsNotNone(run, "Run should be persisted in database")
            self.assertEqual(run.status, "needs_clarification")
            self.assertEqual(run.missing_fields, ["project_description"])
            self.assertEqual(run.intake_data, intake_data)
        finally:
            db.close()

    def test_get_run_by_id_returns_stored_run(self) -> None:
        """Verify that GET /api/agents/runs/{run_id} returns the stored run."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "Early-stage fintech startup",
            "project_description": "Dashboard with MRR and churn charts",
        }

        # Create a run
        create_response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )
        self.assertEqual(create_response.status_code, 201)
        created_run = create_response.json()
        run_id = created_run["run_id"]

        # Retrieve the run by ID
        get_response = client.get(f"/api/agents/runs/{run_id}")

        self.assertEqual(get_response.status_code, 200)
        retrieved_run = get_response.json()
        self.assertEqual(retrieved_run["run_id"], run_id)
        self.assertEqual(retrieved_run["status"], "validated")
        self.assertEqual(retrieved_run["agent_type"], "freelance")
        self.assertEqual(retrieved_run["intake_data"], intake_data)
        self.assertEqual(retrieved_run["missing_fields"], [])

    def test_get_unknown_run_id_returns_404(self) -> None:
        """Verify that GET for an unknown run_id returns 404."""
        fake_run_id = str(uuid.uuid4())

        response = client.get(f"/api/agents/runs/{fake_run_id}")

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("not found", data["detail"].lower())

    def test_created_at_and_updated_at_are_set_on_creation(self) -> None:
        """Verify timestamps are set when run is created."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "Early-stage fintech startup",
            "project_description": "Dashboard with MRR and churn charts",
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])

    def test_run_id_is_unique(self) -> None:
        """Verify that each run gets a unique run_id."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "Early-stage fintech startup",
            "project_description": "Dashboard with MRR and churn charts",
        }

        response1 = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )
        response2 = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        run_id_1 = response1.json()["run_id"]
        run_id_2 = response2.json()["run_id"]
        self.assertNotEqual(run_id_1, run_id_2)
        self.assertEqual(self._run_count(), 2)

    def test_multiple_runs_can_be_retrieved_independently(self) -> None:
        """Verify that multiple runs are stored independently and can be retrieved."""
        intake_data_1 = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "Early-stage fintech startup",
            "project_description": "Dashboard with MRR and churn charts",
        }
        intake_data_2 = {
            "opportunity_title": "Build a Python API",
            "client_description": "Established enterprise",
            "project_description": "REST API with authentication",
        }

        response1 = client.post(
            "/api/agents/freelance/runs",
            json=intake_data_1,
        )
        response2 = client.post(
            "/api/agents/freelance/runs",
            json=intake_data_2,
        )

        run_id_1 = response1.json()["run_id"]
        run_id_2 = response2.json()["run_id"]

        # Retrieve both runs
        get_response_1 = client.get(f"/api/agents/runs/{run_id_1}")
        get_response_2 = client.get(f"/api/agents/runs/{run_id_2}")

        self.assertEqual(get_response_1.status_code, 200)
        self.assertEqual(get_response_2.status_code, 200)

        retrieved_run_1 = get_response_1.json()
        retrieved_run_2 = get_response_2.json()

        # Verify each run has the correct intake data
        self.assertEqual(retrieved_run_1["run_id"], run_id_1)
        self.assertEqual(retrieved_run_2["run_id"], run_id_2)
        self.assertEqual(retrieved_run_1["intake_data"], intake_data_1)
        self.assertEqual(retrieved_run_2["intake_data"], intake_data_2)
        self.assertNotEqual(retrieved_run_1["intake_data"], retrieved_run_2["intake_data"])
        self.assertEqual(self._run_count(), 2)


if __name__ == "__main__":
    unittest.main()
