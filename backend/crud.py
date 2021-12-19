from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from models import Gene, Geneset
from schemas import GenesetCreate, GeneCreate


def get_geneset(db: Session, geneset_id: int):
    db_geneset = db.query(Geneset).filter(Geneset.id == geneset_id).first()
    if not db_geneset:
        raise HTTPException(404)
    return db_geneset


def get_genesets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Geneset).offset(skip).limit(limit).all()


def get_geneset_by_pattern_in_title(db: Session, pattern: str):
    return (
        db.query(Geneset).filter(Geneset.title.like("%" + pattern + "%")).all()
    )


def create_empty_geneset(db: Session, geneset: GenesetCreate):
    db_geneset = Geneset(title=geneset.title)
    db.add(db_geneset)
    db.commit()
    db.refresh(db_geneset)
    return db_geneset


def create_geneset_with_genes(db: Session, geneset: GenesetCreate):
    db_geneset = Geneset(title=geneset.title)
    db.add(db_geneset)
    for gene in geneset.genes:
        db_gene = create_gene(db, gene, db_geneset.id)
        db_geneset.genes.append(db_gene)
    db.commit()
    db.refresh(db_geneset)
    return db_geneset


def update_geneset(
    db: Session, geneset_id: int, title: str, genes: List[GeneCreate]
):
    db_geneset = get_geneset(db, geneset_id)
    db_geneset.title = title
    db.query(Gene).filter(Gene.geneset_id == geneset_id).delete()
    for gene in genes:
        db_gene = create_gene(db, gene, db_geneset.id)
        db_geneset.genes.append(db_gene)
    db.commit()
    db.refresh(db_geneset)
    return db_geneset


def get_genes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Gene).offset(skip).limit(limit).all()


def get_gene_by_name(db: Session, name: str):
    db_gene = db.query(Gene).filter(Gene.name == name).first()
    if not db_gene:
        raise HTTPException(404)
    return db_gene


def get_genes_by_pattern_in_name(db: Session, pattern: str):
    return db.query(Gene).filter(Gene.name.like("%" + pattern + "%")).all()


def create_gene(db: Session, gene: GeneCreate, geneset_id: int):
    db_gene = Gene(**gene.dict(), geneset_id=geneset_id)
    db.add(db_gene)
    db.commit()
    db.refresh(db_gene)
    return db_gene
