import datetime
from fastapi import FastAPI
from app import bazi

app = FastAPI()

@app.get("/")
def read_root():
    return {"message":  bazi.HeavenlyStem.JIA.name + " " + str(bazi.HeavenlyStem.JIA.value) + " " + str(bazi.EarthlyBranchCN[bazi.EarthlyBranch.MAO.name].value)}


@app.get("/year/{year}")
def get_heavenly_branch(year: int):
    heavenly_stem, earthly_branch = bazi.get_heavenly_stem_earthly_branch(year, 1)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch)}

@app.get("/year_january_heavenly_stem/{year}")
def get_heavenly_branch(year: int):
    heavenly_stem = bazi.calculate_month_heavenly(year, 0)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem)}


@app.get("/year/{year}/month/{month}")
def get_heavenly_branch(year: int, month: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly(year, month-1)
    heavenly_stem, earthly_branch = bazi.get_heavenly_stem_earthly_branch(year, month-1)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), 
            "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch), 
            "Heavenly Month Stem": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "Earthly Month Stem": bazi.resolveEarthlyBranch(earthly_month_stem)
            }


@app.get("/year/{year}/month/{month}/day/{day}")
def get_heavenly_branch(year: int, month: int, day: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly(year, month)
    heavenly_stem, earthly_branch = bazi.get_heavenly_stem_earthly_branch(year, month)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly(year, month, day)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), 
            "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch), 
            "Heavenly Month Stem": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "Earthly Month Stem": bazi.resolveEarthlyBranch(earthly_month_stem),
            "Heavenly Day Stem": bazi.resolveHeavenlyStem(heavenly_day_stem),
            "Earthly Day Stem": bazi.resolveEarthlyBranch(earthly_day_stem)
            }


@app.get("/year/{year}/month/{month}/day/{day}/hour/{hour}")
def get_heavenly_branch(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly(year, month)
    heavenly_stem, earthly_branch = bazi.get_heavenly_stem_earthly_branch(year, month)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly(year, month, day)
    heavenly_hour_stem, earthly_hour_stem = bazi.calculate_hour_heavenly(year, month, day, hour)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), 
            "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch), 
            "Heavenly Month Stem": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "Earthly Month Stem": bazi.resolveEarthlyBranch(earthly_month_stem),
            "Heavenly Day Stem": bazi.resolveHeavenlyStem(heavenly_day_stem),
            "Earthly Day Stem": bazi.resolveEarthlyBranch(earthly_day_stem),
            "Heavenly Hour Stem": bazi.resolveHeavenlyStem(heavenly_hour_stem),
            "Earthly Hour Stem": bazi.resolveEarthlyBranch(earthly_hour_stem)
            }


@app.get("/luna_year/{from_year}/to_year/{to_year}")
def get_heavenly_branch(from_year: int, to_year: int):

    current_date = datetime.date(from_year, 1, 1)
    end_date = datetime.date(to_year, 12, 31)

    while current_date <= end_date:
       # Do something with the current_date
        print(current_date.strftime("YYYY-MM-DD"))
        # Move to the next day
        current_date += datetime.timedelta(days=1)


get_heavenly_branch(2023,8,21,9)