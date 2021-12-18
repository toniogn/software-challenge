from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/genesets", response_model=List[schemas.Geneset])
def read_all_genesets(db: Session = Depends(get_db)):
    genesets = crud.get_genesets(db)
    return genesets


@app.get("/genesets/search/{pattern}", response_model=List[schemas.Geneset])
def read_match_genesets(pattern: str, db: Session = Depends(get_db)):
    genesets = crud.get_geneset_by_title(db, pattern)
    return genesets


@app.get("/genesets/{geneset_id}", response_model=schemas.Geneset)
def read_geneset(geneset_id: int, db: Session = Depends(get_db)):
    return crud.get_geneset(db, geneset_id)


@app.put("/genesets/{geneset_id}", response_model=schemas.Geneset)
def update_genesets(
    geneset_id: int,
    geneset: schemas.GenesetCreate,
    db: Session = Depends(get_db),
):
    return crud.update_geneset(db, geneset_id, geneset.title, geneset.genes)


@app.post("/genesets")
def create_geneset(
    geneset: schemas.GenesetCreate, db: Session = Depends(get_db)
):
    db_geneset = crud.create_geneset_with_genes(db, geneset)
    return db_geneset.id


@app.get("/genes/{name}", response_model=List[schemas.Gene])
def read_match_genes(name: str, db: Session = Depends(get_db)):
    gene = crud.get_genes_by_name(db, name)
    return gene
