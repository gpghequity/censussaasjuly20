from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import os, requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Population API is live."}

@app.get("/get_data")
def get_data(state: str = Query(..., min_length=2, max_length=2)):
    fips = {"PA": "42", "NY": "36", "NJ": "34", "OH": "39"}
    if state.upper() not in fips:
        return JSONResponse(status_code=400, content={"error": "Invalid state code"})
    params = {
        "get": "NAME,B01003_001E,B19013_001E",
        "for": "place:*",
        "in": f"state:{fips[state.upper()]}",
        "key": os.getenv("CENSUS_API_KEY")
    }
    r = requests.get("https://api.census.gov/data/2022/acs/acs5", params=params)
    if r.status_code != 200:
        return JSONResponse(status_code=500, content={"error": "Census API failed"})
    data = r.json()[1:]
    return {
        "results": [{
            "city": row[0].replace(f", {state.upper()}", ""),
            "population": int(row[1]),
            "median_income": int(row[2]) if row[2].isdigit() else None
        } for row
