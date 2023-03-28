from pprint import pp
from dataclasses import dataclass
from random import sample
from OSMPythonTools import element

# External
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from OSMPythonTools.api import Api
import pandas as pd

# Typing
from OSMPythonTools.element import Element
from OSMPythonTools.api import ApiResult
from OSMPythonTools.nominatim import NominatimResult
from OSMPythonTools.overpass import OverpassResult

nominatim = Nominatim()
overpass = Overpass()
api = Api()

def build_facts(settlements):
    df = pd.DataFrame(columns=["Comune", "Cibo", "Istruzione", "Natura", "Tempo libero"])

    for region in settlements:
        areaId = nominatim.query(region).areaId()
        query = overpassQueryBuilder(area=areaId, elementType="relation", selector='"admin_level"="4"')

        res: OverpassResult = overpass.query(query)
        res: Element = res.relations()[0]
        areaId = res.areaId() # Area regione

        query = overpassQueryBuilder(area=areaId, elementType="relation", selector='"admin_level"="8"')
        res: OverpassResult = overpass.query(query)

        res = res.relations()
        
        comune: Element
        for i, comune in enumerate(res):
            name = comune.tag("name")
            print(f"{i+1}/{len(res)}: {name}")
            areaId = comune.areaId()

            sustenance = get_sustenance(areaId)
            education = get_education(areaId)
            natural = get_natural(areaId)
            leisure = get_leisure(areaId)

            d = [name, sustenance, education, natural, leisure]
            d = pd.DataFrame(columns=df.columns, data=[d])
            df = pd.concat([df, d], ignore_index=True)

    df.to_csv(f"dati_osm_comuni.csv", index=False)

def get_sustenance(areaId):
    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"amenity"~"restaurant|fast_food|bar|cafe"')
    res: OverpassResult = overpass.query(query)
    return res.countElements()

def get_education(areaId):
    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"amenity"~"college|kindergarten|library|school"')
    res: OverpassResult = overpass.query(query)
    return res.countElements()

def get_natural(areaId):
    tot = 0
    query = overpassQueryBuilder(area=areaId, elementType="relation", selector='"landuse"~"forest|meadow"')
    res: OverpassResult = overpass.query(query)
    tot += res.countElements()

    query = overpassQueryBuilder(area=areaId, elementType="relation", selector='"natural"~"fell|grassland|wood|water"')
    res: OverpassResult = overpass.query(query)
    tot += res.countElements()

    return tot

def get_services(areaId):
    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"amenity"~"courthouse|fire_station|police|post_office"')
    res: OverpassResult = overpass.query(query)
    return res.countElements()

def get_leisure(areaId):
    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"leisure"')
    res: OverpassResult = overpass.query(query)
    return res.countElements()

if __name__=="__main__":
    regioni = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"]
    build_facts(regioni)