from segments.ops import router as ops_router
from fastapi import FastAPI, HTTPException
from segments.segment import InputError, segment

app = FastAPI()
app.include_router(ops_router, prefix="/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/segment")
def post_segment(body: dict):
    try:
        return segment(body.get("rows"), body.get("k", 2))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
