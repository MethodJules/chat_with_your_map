from typing import List, Dict

from pydantic import BaseModel


class Dataset(BaseModel):
    md_id: str
    csw_url: str
    show_doc_url: str
    rs_id: str
    md_name: str
    bbox: str
    kategorie_opendata: List[str]
    kategorie_inspire: List[str]
    kategorie_organisation: str

class Layer(BaseModel):
    id: str
    name: str
    url: str
    typ: str
    featureType: str
    outputFormat: str
    version: str
    featureNS: str
    gfiAttributes: Dict[str, str]
    gfiTheme: str
    layerAttribution: str
    legendURL: str
    datasets: List[Dataset]
    urlIsVisible: bool
