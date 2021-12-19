from typing import List
from pydantic import BaseModel


class GeneBase(BaseModel):
    name: str


class GeneCreate(GeneBase):
    pass


class Gene(GeneBase):
    id: int
    geneset_id: int

    class Config:
        orm_mode = True


class GenesetBase(BaseModel):
    title: str


class GenesetCreate(GenesetBase):
    title: str
    genes: List[GeneBase] = []


class Geneset(GenesetBase):
    id: int
    genes: List[Gene] = []

    class Config:
        orm_mode = True
