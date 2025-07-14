from fastapi import FastAPI, Response
from app.services import get_race_results
import matplotlib.pyplot as plt
import io
import fastf1

app = FastAPI()

@app.get("/test")
def read_race():
    return {"message": "Hello, World!"}

@app.get("/race/{year}/{gp}")
def read_race(year: int, gp: str):
    return get_race_results(year, gp)

@app.get("/race-plot/{year}/{gp_name}")
def race_plot(year: int, gp_name: str):
    session = fastf1.get_session(year, gp_name, 'R')
    session.load()
    laps = session.laps

    classified = session.results[session.results['Position'].notna()]
    top5 = classified.head(5)['Abbreviation'].tolist()

    plt.figure(figsize=(10, 5))
    for driver in top5:
        driver_laps = laps.pick_driver(driver).pick_quicklaps()
        lap_numbers = driver_laps['LapNumber']
        lap_times = driver_laps['LapTime'].dt.total_seconds()
        plt.plot(lap_numbers, lap_times, label=driver)

    plt.xlabel("Volta")
    plt.ylabel("Tempo (segundos)")
    plt.title(f"Tempo por volta - {gp_name.title()} {year}")
    plt.legend()
    plt.tight_layout()

    # Salvar imagem em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")