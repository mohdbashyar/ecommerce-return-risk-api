import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

# Feature column definitions
CATEGORICAL_FEATURES = ['product_category', 'shipping_type']
NUMERICAL_FEATURES = [
    'price',
    'seller_rating',
    'customer_tenure_days',
    'previous_returns_count',
    'is_prime_member',
    'quantity',
    'discount_applied'
]
TARGET_COL = 'returned'

def load_data(root_dir: str) -> pd.DataFrame:
    """Load dataset from Excel or CSV with fallback handling."""
    excel_path = os.path.join(root_dir, 'amazon_returns_dataset_cleaned.xlsx')
    csv_raw_path = os.path.join(root_dir, 'data', 'raw_returns.csv')
    
    if os.path.exists(excel_path):
        print(f"Reading dataset from Excel: {excel_path}")
        df = pd.read_excel(excel_path)
    elif os.path.exists(csv_raw_path):
        print(f"Reading dataset from CSV: {csv_raw_path}")
        df = pd.read_csv(csv_raw_path)
    else:
        raise FileNotFoundError(
            f"Dataset not found at {excel_path} or {csv_raw_path}."
        )

    # Normalize discount column if discount_pct exists instead of discount_applied
    if 'discount_applied' not in df.columns and 'discount_pct' in df.columns:
        df['discount_applied'] = df['discount_pct'] / 100.0 if df['discount_pct'].max() > 1 else df['discount_pct']
    elif 'discount_applied' in df.columns:
        # Ensure discount_applied is normalized between 0.0 and 1.0
        if df['discount_applied'].max() > 1.0:
            df['discount_applied'] = df['discount_applied'] / 100.0

    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset and save raw and processed CSV copies."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save raw CSV copy if not existing
    raw_csv_path = os.path.join(data_dir, 'raw_returns.csv')
    df.to_csv(raw_csv_path, index=False)
    
    # Ensure required columns are present
    required_cols = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET_COL]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")
        
    cleaned_df = df[required_cols].copy()
    
    # Fill missing values
    for col in NUMERICAL_FEATURES:
        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
    for col in CATEGORICAL_FEATURES:
        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
    cleaned_df[TARGET_COL] = cleaned_df[TARGET_COL].astype(int)
    
    processed_csv_path = os.path.join(data_dir, 'processed_returns.csv')
    cleaned_df.to_csv(processed_csv_path, index=False)
    print(f"Cleaned dataset saved to {processed_csv_path} ({len(cleaned_df)} records).")
    
    return cleaned_df

def build_pipeline() -> Pipeline:
    """Construct Scikit-Learn preprocessing and classification pipeline."""
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES),
            ('num', StandardScaler(), NUMERICAL_FEATURES)
        ]
    )
    
    pipeline = Pipeline(
        steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                random_state=42,
                class_weight='balanced'
            ))
        ]
    )
    return pipeline

def train_and_evaluate():
    """Main training routine."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = load_data(root_dir)
    cleaned_df = clean_data(df)
    
    X = cleaned_df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = cleaned_df[TARGET_COL]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} rows | Test set: {X_test.shape[0]} rows")
    
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Export artifacts
    models_dir = os.path.join(root_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    pipeline_path = os.path.join(models_dir, 'pipeline.joblib')
    model_path = os.path.join(models_dir, 'model.joblib')
    
    joblib.dump(pipeline, pipeline_path)
    joblib.dump(pipeline.named_steps['classifier'], model_path)
    
    print(f"\nArtifacts exported successfully:")
    print(f"  - Pipeline: {pipeline_path}")
    print(f"  - Model:    {model_path}")

if __name__ == '__main__':
    train_and_evaluate()
