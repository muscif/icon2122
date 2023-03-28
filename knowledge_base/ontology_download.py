from pprint import pp
from dataclasses import dataclass
from random import sample

# External
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from tabulate import tabulate
from pyswip import Prolog, Functor, Variable, Query, call

# Typing
from OSMPythonTools.element import Element
from OSMPythonTools.api import ApiResult
from OSMPythonTools.nominatim import NominatimResult
from OSMPythonTools.overpass import OverpassResult

nominatim = Nominatim()
overpass = Overpass()

# Tilde ~
def get_accommodations(areaId, print_tab=False):
    elements = set()

    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"tourism"~"hotel|guest_house|apartment"')
    res: OverpassResult = overpass.query(query)
    elements.update(res.elements())

    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"building"~"hotel"')
    res: OverpassResult = overpass.query(query)
    elements.update(res.elements())

    e: Element
    accommodations = set()

    for e in elements:
        name = e.tag("name")
        lat, lon = e.lat(), e.lon()
        phone = e.tag("phone")
        website = e.tag("website")
        email = e.tag("email")
        stars = e.tag("stars")
        wheelchair = e.tag("wheelchair")
        internet_access = e.tag("internet_access")

        t = name, lat, lon, phone, website, email, stars, internet_access, wheelchair
        t = tuple(map(lambda x: str(x), t))

        if all([name, stars]) and any([phone, website, email]):
            accommodations.add(t)

    h = ["name", "lat", "lon", "phone", "website", "email", "stars", "internet_access", "wheelchair"]

    if print_tab:
        print(tabulate(accommodations, missingval="_", maxcolwidths=[30], headers=h))
    
    return accommodations

def get_restaurants(areaId, print_tab=False):
    elements = set()

    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"amenity"="restaurant"')
    res: OverpassResult = overpass.query(query)

    elements.update(res.elements())

    e: Element
    restaurants = set()

    for e in elements:
        name = e.tag("name")
        lat, lon = e.lat(), e.lon()
        phone = e.tag("phone")
        website = e.tag("website")
        email = e.tag("email")
        cuisine = e.tag("cuisine")
        takeaway = e.tag("takeaway")
        delivery = e.tag("delivery")
        opening_hours = e.tag("opening_hours")
        wheelchair = e.tag("wheelchair")

        t = name, lat, lon, phone, website, email, cuisine, takeaway, delivery, opening_hours, wheelchair
        t = tuple(map(lambda x: str(x), t))

        if name and any([phone, website, email]):
            restaurants.add(t)

    h = ["name", "lat", "lon", "phone", "website", "email", "cuisine", "takeaway", "delivery", "opening_hours", "wheelchair"]

    if print_tab:
        print(tabulate(restaurants, missingval="_", maxcolwidths=[30], headers=h))
    
    return restaurants

def get_attractions(areaId, print_tab=False):
    elements = set()

    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"tourism"~"attraction|gallery|museum"')
    res: OverpassResult = overpass.query(query)
    elements.update(res.elements())

    query = overpassQueryBuilder(area=areaId, elementType="node", selector='"historical"')
    res: OverpassResult = overpass.query(query)
    elements.update(res.elements())

    e: Element
    attractions = set()

    for e in elements:
        name = e.tag("name")
        lat, lon = e.lat(), e.lon()
        phone = e.tag("phone")
        website = e.tag("website")
        email = e.tag("email")
        fee = e.tag("fee")
        wheelchair = e.tag("wheelchair")

        t = name, lat, lon, phone, website, email, fee, wheelchair
        t = tuple(map(lambda x: str(x), t))

        if name and any([phone, website, email]):
            attractions.add(t)

    h = ["name", "lat", "lon", "phone", "website", "email", "fee", "wheelchair"]

    if print_tab:
        print(tabulate(attractions, missingval="_", maxcolwidths=[30], headers=h))
    
    return attractions

def build_facts(settlement, admin_level):
    areaId = nominatim.query(settlement).areaId()
    query = overpassQueryBuilder(area=areaId, elementType="relation", selector=f'"admin_level"="{admin_level}"')

    result: OverpassResult = overpass.query(query)
    comune: Element = result.relations()[0]
    areaId = comune.areaId()

    accommodations = list(get_accommodations(areaId))
    restaurants = list(get_restaurants(areaId))
    attractions = list(get_attractions(areaId))

    with open(f"{settlement.lower()}.pl", "w", encoding="utf-8") as facts:
        for name, lat, lon, phone, website, email, stars, internet_access, wheelchair in accommodations:
            name = name.replace("'", "")
            phone = phone if phone not in ("None", None) else "false"
            website = website if website not in ("None", None) else "false"
            email = email if email not in ("None", None) else "false"
            stars = stars.replace("S", "")
            internet_access = "true" if internet_access in ("yes", "wlan") else "false"
            wheelchair = "true" if wheelchair in ("limited", "yes") else "false"
            facts.write(f"accommodation('{name}', {lat}, {lon}, '{phone}', '{website}', '{email}', {stars}, '{internet_access}', '{wheelchair}').\n")

        facts.write("\n")

        for name, lat, lon, phone, website, email, cuisine, takeaway, delivery, opening_hours, wheelchair in restaurants:
            name = name.replace("'", "")
            phone = phone if phone not in ("None", None) else "false"
            website = website if website not in ("None", None) else "false"
            email = email if email not in ("None", None) else "false"
            cuisine = cuisine.lower().replace(" ", "")
            takeaway = "true" if takeaway in ("yes", "only") else "false"
            delivery = "false" if delivery == "no" else "true"
            opening_hours = opening_hours if opening_hours not in ("None", None) else "false"
            wheelchair = "true" if wheelchair in ("limited", "yes") else "false"
            facts.write(f"restaurant('{name}', {lat}, {lon}, '{phone}', '{website}', '{email}', '{cuisine}', '{takeaway}', '{delivery}', '{opening_hours}', '{wheelchair}').\n")

        facts.write("\n")

        for name, lat, lon, phone, website, email, fee, wheelchair in attractions:
            name = name.replace("'", "")
            phone = phone if phone not in ("None", None) else "false"
            website = website if website not in ("None", None) else "false"
            email = email if email not in ("None", None) else "false"
            fee = "false" if fee in ("no", "None") else "true"
            wheelchair = "true" if wheelchair in ("limited", "yes") else "false"
            facts.write(f"attraction('{name}', {lat}, {lon}, '{phone}', '{website}', '{email}', '{fee}', '{wheelchair}').\n")

if __name__=="__main__":
    admin_level = {
        "Berlino": 4,
        "Londra": 5,
        "Parigi": 6,
        "Milano": 8,
    }

    for settlement, level in admin_level.items():
        build_facts(settlement, level)