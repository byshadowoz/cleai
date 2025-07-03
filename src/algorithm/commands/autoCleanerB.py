import pandas as pd
import numpy as np
from io import BytesIO, StringIO

class DataCleaner:
    def __init__(self, file_input, filename=None):
        """
        Two ways to initialize:
        1. Provide a file path as a string (e.g., 'data.csv').
        2. Provide an UploadedFile object (e.g., from FastAPI or Streamlit
        """
        self.df = self.load_data(file_input, filename)
        self.report = {"original_rows": len(self.df), "original_cols": len(self.df.columns)}
    
    def load_data(self, file_input, filename=None):
        
        if isinstance(file_input, str):
            return self._load_from_path(file_input)
        
        elif hasattr(file_input, 'read'):
            return self._load_from_uploaded_file(file_input, filename)
        
        else:
            raise TypeError("Entry must be a file path string or an UploadedFile object")

    def _load_from_path(self, file_path):
        """Load data from a file path"""
        match = file_path.split('.')[-1].lower() if file_path else 'csv'
        if match == 'csv':
            return pd.read_csv(file_path)
        elif match in ['xlsx', 'xls']:
            return pd.read_excel(file_path)
        

    def _load_from_uploaded_file(self, uploaded_file, filename):
        """Load data from an UploadedFile object"""

        extension = filename.split('.')[-1].lower() if filename else 'csv'
        

        content = uploaded_file.read()
        
        if extension == 'csv':

            return pd.read_csv(StringIO(content.decode('utf-8')))
        elif extension in ['xlsx', 'xls']:

            return pd.read_excel(BytesIO(content))
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
            
    def auto_clean(self):
        """Execute all cleaning steps"""
        self.clean_headers()
        self.drop_empty()
        self.handle_duplicates()
        self.remove_trims()
        self.fix_data_types()
        self.handle_missing()
        self.remove_constant_columns()
        return self.df, self.report

    def clean_headers(self):
        """Normalize column headers"""
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace('[^\w]', '', regex=True)
        )
        self.report['renamed_columns'] = list(self.df.columns)

    def drop_empty(self, threshold=0.7):
        """Drop empty columns and rows based on a threshold"""
        # Threshold for dropping columns: if more than 70% of values are null, drop
        col_null_ratio = self.df.isnull().mean()
        cols_to_drop = col_null_ratio[col_null_ratio > threshold].index
        self.df.drop(columns=cols_to_drop, inplace=True)
        self.report['dropped_cols'] = list(cols_to_drop)
        
        # Threshold for dropping rows: if more than 70% of values are null, drop
        self.df.dropna(thresh=len(self.df.columns)*0.7, inplace=True)
        self.report['remaining_rows'] = len(self.df)

    def handle_duplicates(self):
        """Manage duplicates in the dataset"""
        duplicates = self.df.duplicated().sum()
        self.df.drop_duplicates(inplace=True)
        self.report['duplicates_removed'] = duplicates

    def fix_data_types(self):
        """Convert columns to appropriate data types"""
        for col in self.df.select_dtypes(include='object'):
            try:
                self.df[col] = pd.to_datetime(self.df[col])
                self.report.setdefault('converted_to_datetime', []).append(col)
            except:
                try:
                    self.df[col] = pd.to_numeric(self.df[col])
                    self.report.setdefault('converted_to_numeric', []).append(col)
                except:
                    pass

    def handle_missing(self):
        """Handle missing values in the dataset"""
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                else:
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
                self.report.setdefault('imputed_cols', {})[col] = self.df[col].dtype.name

    def remove_constant_columns(self):
        """Remove columns with constant values (only one unique value)"""
        constant_cols = [col for col in self.df.columns if self.df[col].nunique() == 1]
        self.df.drop(columns=constant_cols, inplace=True)
        self.report['constant_cols_removed'] = constant_cols

    def remove_trims(self):
        """Remove leading and trailing whitespace from string columns"""
        for col in self.df.select_dtypes(include='object'):
            self.df[col] = self.df[col].str.strip()
        # Store the names of trimmed columns in the report
        if 'trimmed_columns' not in self.report:
            self.report['trimmed_columns'] = []
        if 'trimmed_columns' in self.report:
            self.report['trimmed_columns'].extend(
                [col for col in self.df.select_dtypes(include='object').columns if col not in self.report['trimmed_columns']]
            )
        self.report['trimmed_columns'] = list(self.df.select_dtypes(include='object').columns)