from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas import SimulationRequest, SimulationResponse, SweepRequest, SweepResponse
from app.services import run_simulation

app = FastAPI(title="Monte Carlo Pricing Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/simulate", response_model=SimulationResponse)
def price_option(req: SimulationRequest):
    params = dict(req.parameters)
    result = run_simulation(req.scenario, params)
    return {"result": result}

@app.post("/sweep", response_model=SweepResponse)
def sweep(req: SweepRequest):
    points = []
    for n in req.sample_sizes:
        params = dict(req.parameters)  
        params["n_samples"] = n

        result = run_simulation(req.scenario, params)

        points.append({
            "n": n,
            **result
        })

    return {"points": points}