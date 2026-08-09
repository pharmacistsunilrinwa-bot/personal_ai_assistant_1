import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union

class DataAnalysisService:
    def __init__(self):
        pass

    def _load_data(self, data_source: Union[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        """Helper to load data from a file path or list of dictionaries into a DataFrame."""
        if isinstance(data_source, str):
            if not os.path.exists(data_source):
                raise FileNotFoundError(f"File not found: {data_source}")
            
            ext = os.path.splitext(data_source)[-1].lower()
            if ext == '.csv':
                return pd.read_csv(data_source)
            elif ext == '.json':
                return pd.read_json(data_source)
            elif ext in ['.xlsx', '.xls']:
                return pd.read_excel(data_source)
            else:
                raise ValueError("Unsupported file format. Please use CSV, JSON, or Excel.")
        elif isinstance(data_source, list):
            return pd.DataFrame(data_source)
        else:
            raise TypeError("Data source must be a file path (str) or a list of dictionaries.")

    def get_summary(self, data_source: Union[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generates comprehensive summary statistics and structural info of a dataset."""
        df = self._load_data(data_source)
        
        # Structure information
        shape = df.shape
        columns_info = {}
        for col in df.columns:
            columns_info[col] = {
                "type": str(df[col].dtype),
                "non_null_count": int(df[col].notnull().sum()),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique())
            }
        
        # Summary statistics (numeric)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_summary = {}
        if numeric_cols:
            summary_df = df[numeric_cols].describe()
            # Convert NaN to None for JSON safety
            summary_df = summary_df.replace({np.nan: None})
            numeric_summary = summary_df.to_dict()

        # Categorical summaries
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        categorical_summary = {}
        for col in categorical_cols:
            top_value = df[col].mode().tolist()
            categorical_summary[col] = {
                "most_common": top_value[0] if top_value else None,
                "unique_values_sample": df[col].dropna().unique()[:5].tolist()
            }
            
        return {
            "num_rows": shape[0],
            "num_cols": shape[1],
            "columns": columns_info,
            "numeric_summary": numeric_summary,
            "categorical_summary": categorical_summary
        }

    def clean_data(
        self, 
        data_source: Union[str, List[Dict[str, Any]]], 
        strategy: str = "drop", 
        fill_value: Any = None,
        remove_duplicates: bool = True
    ) -> List[Dict[str, Any]]:
        """Cleans the dataset by handling missing values and duplicate rows."""
        df = self._load_data(data_source)
        
        if remove_duplicates:
            df = df.drop_duplicates()
            
        if strategy == "drop":
            df = df.dropna()
        elif strategy == "fill":
            if fill_value is not None:
                df = df.fillna(fill_value)
            else:
                # Fallback: fill numeric with mean, categorical with mode
                for col in df.columns:
                    if np.issubdtype(df[col].dtype, np.number):
                        df[col] = df[col].fillna(df[col].mean())
                    else:
                        mode_val = df[col].mode()
                        if not mode_val.empty:
                            df[col] = df[col].fillna(mode_val[0])
                            
        # Convert any remaining NaN to None for JSON safety
        df = df.replace({np.nan: None})
        return df.to_dict(orient="records")

    def aggregate_data(
        self, 
        data_source: Union[str, List[Dict[str, Any]]], 
        group_by_col: str, 
        agg_rules: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Groups data by a column and aggregates specified columns with sum, mean, count etc.
        
        Example agg_rules: {"sales": "sum", "age": "mean"}
        """
        df = self._load_data(data_source)
        
        if group_by_col not in df.columns:
            raise ValueError(f"Grouping column '{group_by_col}' not found in dataset.")
            
        for col in agg_rules.keys():
            if col not in df.columns:
                raise ValueError(f"Aggregation column '{col}' not found in dataset.")
                
        agg_df = df.groupby(group_by_col).agg(agg_rules).reset_index()
        agg_df = agg_df.replace({np.nan: None})
        return agg_df.to_dict(orient="records")

    def calculate_correlations(self, data_source: Union[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, float]]:
        """Calculates Pearson correlation matrix for numeric columns."""
        df = self._load_data(data_source)
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {}
            
        corr_matrix = numeric_df.corr().replace({np.nan: None}).to_dict()
        return corr_matrix

    def detect_outliers(self, data_source: Union[str, List[Dict[str, Any]]], column: str, threshold: float = 1.5) -> Dict[str, Any]:
        """Detects outliers in a numeric column using the Interquartile Range (IQR) method."""
        df = self._load_data(data_source)
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found.")
            
        if not np.issubdtype(df[column].dtype, np.number):
            raise TypeError(f"Column '{column}' must be numeric for outlier detection.")
            
        col_data = df[column].dropna()
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - (threshold * iqr)
        upper_bound = q3 + (threshold * iqr)
        
        outliers_df = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        outliers_df = outliers_df.replace({np.nan: None})
        
        return {
            "column": column,
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "num_outliers": len(outliers_df),
            "outliers": outliers_df.to_dict(orient="records")
        }
