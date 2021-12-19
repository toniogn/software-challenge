import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from main import app, get_db
from database import Base, build_database


TestingSessionLocal, engine = build_database("test_database")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class TestApp(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.first_geneset_data = {
            "id": 1,
            "title": "Test Geneset 1",
            "genes": [{"geneset_id": 1, "id": 1, "name": "dummy_1"}],
        }
        self.second_geneset_data = {
            "id": 2,
            "title": "Test Geneset 2",
            "genes": [{"geneset_id": 2, "id": 2, "name": "dummy_2"}],
        }

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=engine)

    def test_create_geneset_integrity(self):
        response = self.client.post("/genesets", json=self.first_geneset_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 1)

    def test_read_geneset_unknown_raises_404(self):
        response = self.client.get("/genesets/1")
        self.assertEqual(response.status_code, 404)

    def test_read_geneset_integrity(self):
        self.client.post("/genesets", json=self.first_geneset_data)
        response = self.client.get("/genesets/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            self.first_geneset_data,
        )

    def test_read_all_genesets_integrity(self):
        self.client.post("/genesets", json=self.first_geneset_data)
        self.client.post("/genesets", json=self.second_geneset_data)
        response = self.client.get("/genesets")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [self.first_geneset_data, self.second_geneset_data],
        )

    def test_read_match_gensets_with_no_match_integrity(self):
        response = self.client.get("/genesets/search/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_read_match_gensets_with_a_match_integrity(self):
        self.client.post("/genesets", json=self.first_geneset_data)
        self.client.post("/genesets", json=self.second_geneset_data)
        response = self.client.get("/genesets/search/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.second_geneset_data])

    def test_update_geneset_unknown_raises_404(self):
        response = self.client.put("/genesets/1", json=self.first_geneset_data)
        self.assertEqual(response.status_code, 404)

    def test_update_geneset_integrity(self):
        self.client.post("/genesets", json=self.first_geneset_data)
        modified_first_geneset_data = self.first_geneset_data
        modified_first_geneset_gene_data: dict = modified_first_geneset_data[
            "genes"
        ][0]
        modified_first_geneset_gene_data.update({"name": "modified_dummy_1"})
        modified_first_geneset_data.update(
            {
                "title": "Modified Test Geneset 1",
                "genes": [modified_first_geneset_gene_data],
            }
        )
        response = self.client.put(
            "/genesets/1", json=modified_first_geneset_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), modified_first_geneset_data)

    def test_read_gene_by_name_unknown_raises_404(self):
        response = self.client.get("/genes/1")
        self.assertEqual(response.status_code, 404)

    def test_read_gene_by_name_integrity(self):
        self.client.post("/genesets", json=self.first_geneset_data)
        response = self.client.get("/genes/dummy_1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.first_geneset_data["genes"][0])

    def test_read_match_genes_with_no_match_integrity(self):
        response = self.client.get("/genes/search/not_dummy")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_read_match_genes_with_a_match_integrity(self):
        self.client.post("/genesets", json=self.first_geneset_data)
        self.client.post("/genesets", json=self.second_geneset_data)
        response = self.client.get("/genes/search/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), [self.second_geneset_data["genes"][0]]
        )


if __name__ == "__main__":
    unittest.main()
