from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Union, Optional
from services.data_analysis_service import DataAnalysisService

router = APIRouter()
analysis_service = DataAnalysisService()

class DataAnalysisRequest(BaseModel):
    file_path: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None

    def get_source(self) -> Union[str, List[Dict[str, Any]]]:
        if self.file_path:
            return self.file_path
        if self.data is not None:
            return self.data
        raise HTTPException(status_code=400, detail="Either 'file_path' or 'data' must be provided.")

class CleanDataRequest(DataAnalysisRequest):
    strategy: str = "drop" # "drop" or "fill"
    fill_value: Optional[Any] = None
    remove_duplicates: bool = True

class AggregateDataRequest(DataAnalysisRequest):
    group_by_col: str
    agg_rules: Dict[str, str] # e.g. {"sales": "sum", "age": "mean"}

class OutliersRequest(DataAnalysisRequest):
    column: str
    threshold: float = 1.5

@router.post("/summary")
def get_summary(req: DataAnalysisRequest):
    """Retrieves structural and numerical summaries of the given dataset."""
    try:
        source = req.get_source()
        summary = analysis_service.get_summary(source)
        return summary
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clean")
def clean_data(req: CleanDataRequest):
    """Cleans a dataset by removing duplicates or filling/dropping empty cells."""
    try:
        source = req.get_source()
        cleaned_records = analysis_service.clean_data(
            data_source=source,
            strategy=req.strategy,
            fill_value=req.fill_value,
            remove_duplicates=req.remove_duplicates
        )
        return {"status": "success", "data": cleaned_records}
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/aggregate")
def aggregate_data(req: AggregateDataRequest):
    """Aggregates a dataset after grouping by a specified column."""
    try:
        source = req.get_source()
        aggregated_records = analysis_service.aggregate_data(
            data_source=source,
            group_by_col=req.group_by_col,
            agg_rules=req.agg_rules
        )
        return {"status": "success", "data": aggregated_records}
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/correlations")
def calculate_correlations(req: DataAnalysisRequest):
    """Calculates Pearson correlation matrix for numerical columns."""
    try:
        source = req.get_source()
        corr_matrix = analysis_service.calculate_correlations(source)
        return {"correlations": corr_matrix}
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/outliers")
def detect_outliers(req: OutliersRequest):
    """Detects numeric outliers in a specific column using the IQR technique."""
    try:
        source = req.get_source()
        outliers_result = analysis_service.detect_outliers(
            data_source=source,
            column=req.column,
            threshold=req.threshold
        )
        return outliers_result
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except (ValueError, TypeError) as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
