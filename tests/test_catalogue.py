"""Service catalogue and nearest-centre search."""


def test_lists_all_services(client):
    svcs = client.get("/api/services").json()
    assert len(svcs) == 19


def test_service_names_localised(client):
    names = {s["code"]: s["name"] for s in client.get("/api/services?lang=te").json()}
    assert names["INC"] == "ఆదాయ ధృవీకరణ పత్రం"


def test_search_in_telugu(client):
    svcs = client.get("/api/services", params={"q": "కుల"}).json()
    assert svcs and svcs[0]["code"] == "CST"


def test_service_detail_and_missing(client):
    first = client.get("/api/services").json()[0]
    d = client.get(f"/api/services/{first['id']}").json()
    assert d["documents"] and d["eligibility"]
    assert client.get("/api/services/9999").status_code == 404


def test_nearest_centre_by_location(client):
    rows = client.get("/api/centres", params={"lat": 17.4720, "lng": 78.3110, "limit": 3}).json()
    assert rows[0]["name"] == "MeeSeva Centre, Nallagandla"
    assert rows[0]["distance_km"] < rows[1]["distance_km"]


def test_centres_by_district(client):
    hyd = next(d for d in client.get("/api/districts").json() if d["name_en"] == "Hyderabad")
    rows = client.get("/api/centres", params={"district_id": hyd["id"]}).json()
    assert rows and all(r["district"] == "Hyderabad" for r in rows)


def test_invalid_coordinates_rejected(client):
    assert client.get("/api/centres", params={"lat": 200, "lng": 0}).status_code == 422
