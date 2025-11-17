import dask.dataframe as dd
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


def clean_data(dfc, drop_keywords=None, target_col='Label'):
    """Drop id/IP/Timestamp columns, handle missing/inf, drop duplicates."""
    if drop_keywords is None:
        drop_keywords = ['id', 'ID', 'IP', 'Timestamp']
    # build list of columns to drop
    to_drop = [c for c in dfc.columns if any(k in c for k in drop_keywords)]
    # don't drop the target if it's matched accidentally
    to_drop = [c for c in to_drop if c != target_col]
    dfc = dfc.drop(columns=to_drop, errors='ignore')
    # Replace inf with NaN and impute numeric medians
    numeric_cols = dfc.select_dtypes(include=[np.number]).columns.tolist()
    dfc = dfc.replace([np.inf, -np.inf], np.nan)
    if len(numeric_cols) > 0:
        medians = dfc[numeric_cols].median()
        dfc[numeric_cols] = dfc[numeric_cols].fillna(medians)
    # For object columns fillna with empty string (or choose other strategy)
    obj_cols = dfc.select_dtypes(include=['object']).columns.tolist()
    if obj_cols:
        dfc[obj_cols] = dfc[obj_cols].fillna('')
    # Drop duplicates
    dfc = dfc.drop_duplicates()
    return dfc

def remove_highly_correlated(df, threshold=0.95, exclude_cols=None):
    """Remove one of each pair of features with absolute correlation > threshold."""
    if exclude_cols is None:
        exclude_cols = []
    numeric = df.select_dtypes(include=[np.number]).copy()
    numeric = numeric.drop(columns=[c for c in exclude_cols if c in numeric.columns], errors='ignore')
    if numeric.shape[1] < 2:
        return df
    corr = numeric.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return df.drop(columns=to_drop, errors='ignore')

def encode_and_split(df, target='Label', test_size=0.2, val_ratio_of_train=0.2, random_state=42):
    """Encode categorical features and split into train/val/test sets. Returns numpy arrays for TabNet."""
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataframe")
    X = df.drop(columns=[target])
    y = df[target].copy()

    # Encode categorical features
    categorical_columns = X.select_dtypes(include=['object']).columns.tolist()
    encoders = {}
    for col in categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    # Encode target if it's object
    label_encoder = None
    if y.dtype == object or y.dtype.name == 'category':
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y.astype(str))

    # First split: test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y if len(np.unique(y))>1 else None
    )
    # Second split: train/val from X_temp
    val_size = val_ratio_of_train
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size, random_state=random_state, stratify=y_temp if len(np.unique(y_temp))>1 else None
    )

    # Convert to float32 for TabNet and return numpy arrays
    X_train = X_train.astype(np.float32)
    X_val = X_val.astype(np.float32)
    X_test = X_test.astype(np.float32)

    return {
        'X_train': X_train.values, 'X_val': X_val.values, 'X_test': X_test.values,
        'y_train': y_train, 'y_val': y_val, 'y_test': y_test,
        'feature_columns': X.columns.tolist(),
        'categorical_encoders': encoders,
        'label_encoder': label_encoder
    }