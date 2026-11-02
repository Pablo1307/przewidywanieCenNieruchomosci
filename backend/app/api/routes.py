from fastapi import APIRouter, Depends, HTTPException

from app.schemas.property import Prediction, PropertyFeatures
from app.services.model_service import ModelService, get_model_service

router = APIRouter(prefix="/api")


@router.get("/health")
def health(service: ModelService = Depends(get_model_service)):
    try:
        service.load()
        ready = True
    except HTTPException:
        ready = False
    return {"status": "ok", "model_ready": ready}


@router.get("/features")
def features():
    return {"schema": PropertyFeatures.model_json_schema(), "units": "USD, ft² (1 ft² = 0,092903 m²)", "location": "Ames, Iowa, USA"}


@router.get("/model/info")
def model_info(service: ModelService = Depends(get_model_service)):
    service.load()
    return {key: service.metadata[key] for key in ["selected_model", "version", "dataset", "currency", "features", "train_rows", "test_rows", "selection_metric"]}


@router.get("/model/metrics")
def model_metrics(service: ModelService = Depends(get_model_service)):
    service.load()
    return {key: service.metadata[key] for key in ["comparison", "test", "selected_model", "version", "folds"]}


@router.get("/data/eda")
def eda(service: ModelService = Depends(get_model_service)):
    service.load()
    return service.eda


@router.post("/predict", response_model=Prediction)
def predict(features: PropertyFeatures, service: ModelService = Depends(get_model_service)):
    return service.predict(features.model_dump())
