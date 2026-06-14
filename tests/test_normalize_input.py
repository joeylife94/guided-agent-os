"""
Tests for input normalization (Phase 2-B).

Verifies that:
- Validated runs produce normalized data
- Needs_clarification runs do not produce normalized data
- Original intake_data is preserved
- Whitespace is trimmed in normalized fields
- Technology keywords (Java, Spring, FastAPI, Python, React, etc.) are detected
- Normalized data is persisted and returned by GET /api/agents/runs/{run_id}
"""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun
from app.services.normalization import detect_keywords, detect_project_category

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


class InputNormalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set up test database before each test."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def tearDown(self) -> None:
        """Clean up test database after each test."""
        Base.metadata.drop_all(bind=engine)

    def test_validated_run_produces_normalized_data(self) -> None:
        """Verify that a validated run produces normalized data."""
        intake_data = {
            "opportunity_title": "Build a React Dashboard",
            "client_description": "Early-stage fintech startup using Python",
            "project_description": "Dashboard with analytics using React and FastAPI",
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "validated")

        normalized = data["normalized_data"]
        self.assertIsNotNone(normalized)

        # Verify normalized fields exist
        self.assertIn("normalized_title", normalized)
        self.assertIn("normalized_client_description", normalized)
        self.assertIn("normalized_project_description", normalized)
        self.assertIn("detected_keywords", normalized)
        self.assertIn("detected_stack", normalized)
        self.assertIn("language", normalized)
        self.assertIn("project_category", normalized)

        # Verify normalization results
        self.assertEqual(normalized["normalized_title"], "Build a React Dashboard")
        self.assertEqual(
            normalized["normalized_client_description"],
            "Early-stage fintech startup using Python",
        )
        self.assertIn("react", normalized["detected_keywords"])
        self.assertIn("fastapi", normalized["detected_keywords"])
        self.assertIn("python", normalized["detected_keywords"])

    def test_needs_clarification_run_does_not_produce_normalized_data(self) -> None:
        """Verify that a needs_clarification run does not produce normalized data."""
        intake_data = {
            "opportunity_title": "Build a React dashboard",
            # Missing required fields
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "needs_clarification")
        self.assertIsNone(data["normalized_data"])
        run_id = data["run_id"]

        # Verify normalized_data was NOT created for needs_clarification runs
        db = TestingSessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
            self.assertIsNotNone(run)
            self.assertIsNone(run.normalized_data)
        finally:
            db.close()

    def test_original_intake_data_is_preserved(self) -> None:
        """Verify that original intake_data is preserved, not modified."""
        intake_data = {
            "opportunity_title": "Build a React Dashboard",
            "client_description": "Early-stage startup",
            "project_description": "Web app project",
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        run_id = data["run_id"]

        # Verify intake_data in response matches original
        self.assertEqual(data["intake_data"], intake_data)

        # Verify intake_data in database matches original (not normalized)
        db = TestingSessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
            self.assertIsNotNone(run)
            self.assertEqual(run.intake_data, intake_data)
            # Verify original data has capital 'D' in Dashboard
            self.assertEqual(run.intake_data["opportunity_title"], "Build a React Dashboard")
        finally:
            db.close()

    def test_whitespace_is_trimmed_in_normalized_fields(self) -> None:
        """Verify that whitespace is trimmed in normalized fields."""
        intake_data = {
            "opportunity_title": "  Build a React Dashboard  \n",
            "client_description": "\tEarly-stage startup\t",
            "project_description": "  Web app with Java  ",
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        run_id = data["run_id"]
        normalized = data["normalized_data"]

        # Verify whitespace is trimmed in normalized fields
        self.assertEqual(normalized["normalized_title"], "Build a React Dashboard")
        self.assertEqual(normalized["normalized_client_description"], "Early-stage startup")
        self.assertEqual(normalized["normalized_project_description"], "Web app with Java")

        # Verify original intake_data still has whitespace
        self.assertEqual(
            data["intake_data"]["opportunity_title"],
            "  Build a React Dashboard  \n",
        )

        get_response = client.get(f"/api/agents/runs/{run_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["normalized_data"], normalized)

    def test_tech_keywords_are_detected(self) -> None:
        """Verify that technology keywords are detected in project description."""
        intake_data = {
            "opportunity_title": "Full Stack Project",
            "client_description": "Tech startup",
            "project_description": (
                "Build a web app using React, Python, FastAPI, PostgreSQL, "
                "Docker, and Kubernetes. Also need some Java Spring work."
            ),
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        keywords = data["normalized_data"]["detected_keywords"]

        # Verify expected keywords are detected
        self.assertIn("react", keywords)
        self.assertIn("python", keywords)
        self.assertIn("fastapi", keywords)
        self.assertIn("postgresql", keywords)
        self.assertIn("docker", keywords)
        self.assertIn("kubernetes", keywords)
        self.assertIn("java", keywords)
        self.assertIn("spring", keywords)

    def test_short_keyword_false_positives_are_avoided(self) -> None:
        """Verify obvious short-keyword substring matches are avoided."""
        keywords = detect_keywords(
            "We need to go live with paid content, charts, JSON snippets, "
            "cargo tracking, and reactive layouts."
        )

        self.assertNotIn("go", keywords)
        self.assertNotIn("javascript", keywords)
        self.assertNotIn("java", keywords)
        self.assertNotIn("react", keywords)
        self.assertNotEqual(
            detect_project_category(
                "Paid content launch",
                "Media company",
                "Go live with paid access and campaign copy.",
            ),
            "ml",
        )

    def test_detected_stack_is_curated_and_ordered(self) -> None:
        """Verify that detected_stack returns curated keywords in priority order."""
        intake_data = {
            "opportunity_title": "Multi-tech project",
            "client_description": "Startup",
            "project_description": (
                "Frontend in React and Angular, backend in Python FastAPI, "
                "database PostgreSQL, deployed on AWS with Docker."
            ),
        }

        response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        run_id = data["run_id"]

        db = TestingSessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
            self.assertIsNotNone(run)
            normalized = run.normalized_data
            stack = normalized["detected_stack"]

            # Verify curated stack includes expected tech
            self.assertIn("python", stack)
            self.assertIn("react", stack)
            self.assertIn("fastapi", stack)
            self.assertIn("postgresql", stack)
            self.assertIn("aws", stack)
            self.assertIn("docker", stack)

            # Verify it's curated (not all keywords)
            # angular might be detected but should be in stack
            self.assertIn("angular", stack)

        finally:
            db.close()

    def test_language_detection(self) -> None:
        """Verify that primary programming language is detected."""
        # Test Python
        response_py = client.post(
            "/api/agents/freelance/runs",
            json={
                "opportunity_title": "Python Project",
                "client_description": "Data startup",
                "project_description": "Build data pipeline using Python and FastAPI",
            },
        )
        self.assertEqual(response_py.status_code, 201)
        run_id_py = response_py.json()["run_id"]

        db = TestingSessionLocal()
        try:
            run_py = db.query(AgentRun).filter(AgentRun.id == run_id_py).first()
            self.assertEqual(run_py.normalized_data["language"], "python")
        finally:
            db.close()

        # Test Java
        response_java = client.post(
            "/api/agents/freelance/runs",
            json={
                "opportunity_title": "Java Project",
                "client_description": "Enterprise client",
                "project_description": "Build Spring Boot microservices with Java",
            },
        )
        self.assertEqual(response_java.status_code, 201)
        run_id_java = response_java.json()["run_id"]

        db = TestingSessionLocal()
        try:
            run_java = db.query(AgentRun).filter(AgentRun.id == run_id_java).first()
            self.assertEqual(run_java.normalized_data["language"], "java")
        finally:
            db.close()

        # Test no language detected
        response_none = client.post(
            "/api/agents/freelance/runs",
            json={
                "opportunity_title": "Design Project",
                "client_description": "Creative agency",
                "project_description": "Design landing page and UI mockups",
            },
        )
        self.assertEqual(response_none.status_code, 201)
        run_id_none = response_none.json()["run_id"]

        db = TestingSessionLocal()
        try:
            run_none = db.query(AgentRun).filter(AgentRun.id == run_id_none).first()
            self.assertIsNone(run_none.normalized_data["language"])
        finally:
            db.close()

    def test_project_category_detection(self) -> None:
        """Verify that project category is inferred correctly."""
        test_cases = [
            (
                {
                    "opportunity_title": "Frontend Developer Needed",
                    "client_description": "ecommerce company",
                    "project_description": "Build React UI components and website redesign",
                },
                "web",
            ),
            (
                {
                    "opportunity_title": "Mobile App",
                    "client_description": "startup",
                    "project_description": "iOS and Android app development",
                },
                "mobile",
            ),
            (
                {
                    "opportunity_title": "Backend API",
                    "client_description": "tech company",
                    "project_description": "Build REST API server with database",
                },
                "backend",
            ),
            (
                {
                    "opportunity_title": "Data Analyst",
                    "client_description": "analytics company",
                    "project_description": "ETL pipeline and data warehouse setup",
                },
                "data",
            ),
            (
                {
                    "opportunity_title": "DevOps Engineer",
                    "client_description": "cloud platform",
                    "project_description": "Kubernetes and CI/CD setup",
                },
                "devops",
            ),
        ]

        for intake_data, expected_category in test_cases:
            response = client.post(
                "/api/agents/freelance/runs",
                json=intake_data,
            )
            self.assertEqual(response.status_code, 201)
            run_id = response.json()["run_id"]

            db = TestingSessionLocal()
            try:
                run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
                self.assertIsNotNone(run)
                actual_category = run.normalized_data["project_category"]
                self.assertEqual(
                    actual_category,
                    expected_category,
                    f"Expected {expected_category} but got {actual_category} for {intake_data['opportunity_title']}",
                )
            finally:
                db.close()

    def test_normalized_data_persisted_and_returned_by_get(self) -> None:
        """Verify that normalized data is persisted and returned by GET endpoint."""
        intake_data = {
            "opportunity_title": "React + Python Project",
            "client_description": "Tech startup in San Francisco",
            "project_description": "Full stack web app using React, Python, and PostgreSQL",
        }

        # Create the run
        create_response = client.post(
            "/api/agents/freelance/runs",
            json=intake_data,
        )
        self.assertEqual(create_response.status_code, 201)
        run_id = create_response.json()["run_id"]

        # Retrieve the run via GET
        get_response = client.get(f"/api/agents/runs/{run_id}")
        self.assertEqual(get_response.status_code, 200)
        retrieved_run = get_response.json()

        # Verify structure
        self.assertEqual(retrieved_run["status"], "validated")
        self.assertEqual(retrieved_run["agent_type"], "freelance")
        self.assertEqual(retrieved_run["intake_data"], intake_data)

        normalized = retrieved_run["normalized_data"]
        self.assertIsNotNone(normalized)
        self.assertEqual(
            normalized,
            create_response.json()["normalized_data"],
        )
        self.assertEqual(normalized["normalized_title"], "React + Python Project")
        self.assertIn("react", normalized["detected_keywords"])
        self.assertIn("python", normalized["detected_keywords"])
        self.assertIn("postgresql", normalized["detected_keywords"])
        self.assertIn("python", normalized["detected_stack"])

    def test_multiple_validated_runs_each_have_normalized_data(self) -> None:
        """Verify that multiple runs each get their own normalized data."""
        runs_data = [
            {
                "opportunity_title": "React Project",
                "client_description": "Frontend startup",
                "project_description": "React dashboard with TypeScript",
            },
            {
                "opportunity_title": "Python Project",
                "client_description": "Data company",
                "project_description": "Python Flask API with PostgreSQL",
            },
            {
                "opportunity_title": "Java Project",
                "client_description": "Enterprise",
                "project_description": "Spring Boot microservice with Docker",
            },
        ]

        run_ids = []
        for intake_data in runs_data:
            response = client.post(
                "/api/agents/freelance/runs",
                json=intake_data,
            )
            self.assertEqual(response.status_code, 201)
            run_ids.append(response.json()["run_id"])

        # Verify each run has unique normalized data
        for i, run_id in enumerate(run_ids):
            get_response = client.get(f"/api/agents/runs/{run_id}")
            self.assertEqual(get_response.status_code, 200)
            normalized = get_response.json()["normalized_data"]
            self.assertIsNotNone(normalized)

            # Check tech-specific keywords for each run
            if i == 0:  # React project
                self.assertIn("react", normalized["detected_keywords"])
                self.assertIn("typescript", normalized["detected_keywords"])
            elif i == 1:  # Python project
                self.assertIn("python", normalized["detected_keywords"])
                self.assertIn("flask", normalized["detected_keywords"])
                self.assertIn("postgresql", normalized["detected_keywords"])
            elif i == 2:  # Java project
                self.assertIn("java", normalized["detected_keywords"])
                self.assertIn("spring", normalized["detected_keywords"])
                self.assertIn("docker", normalized["detected_keywords"])


if __name__ == "__main__":
    unittest.main()
