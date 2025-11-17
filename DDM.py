import dask.dataframe as dd
import dask.array as da
from dask.distributed import Client
from dask_ml.model_selection import train_test_split
from dask_ml.xgboost  import XGBRegressor 
from dask_ml.linear_model import LogisticRegression
import pandas as pd
import numpy as np

# Step 1: Start Dask Client (creates local cluster)
client = Client(n_workers=3, threads_per_worker=2)
print(f"Dashboard: {client.dashboard_link}")

# Step 2: Create 3 separate datasets
print("Creating datasets...")
df1 = pd.DataFrame({
    'feature1': np.random.randn(50000),
    'feature2': np.random.randn(50000),
    'target': np.random.randint(0, 2, 50000)
})

df2 = pd.DataFrame({
    'feature1': np.random.randn(50000),
    'feature2': np.random.randn(50000),
    'target': np.random.randint(0, 2, 50000)
})

df3 = pd.DataFrame({
    'feature1': np.random.randn(50000),
    'feature2': np.random.randn(50000),
    'target': np.random.randint(0, 2, 50000)
})

# Convert to Dask DataFrames (distributed across workers)
dask_df1 = dd.from_pandas(df1, npartitions=10)
dask_df2 = dd.from_pandas(df2, npartitions=10)
dask_df3 = dd.from_pandas(df3, npartitions=10)

# Step 3: Train models on different datasets
print("Training models in parallel...")

# Model 1 on dataset 1
X1 = dask_df1[['feature1', 'feature2']]
y1 = dask_df1['target']
model1 = XGBRegressor(n_estimators=50, random_state=42)
model1.fit(X1, y1)

# Model 2 on dataset 2
X2 = dask_df2[['feature1', 'feature2']]
y2 = dask_df2['target']
model2 = XGBRegressor(n_estimators=50, random_state=43)
model2.fit(X2, y2)

# Model 3 on dataset 3
X3 = dask_df3[['feature1', 'feature2']]
y3 = dask_df3['target']
model3 = LogisticRegression(random_state=42)
model3.fit(X3, y3)

print("✓ All models trained!")

# Step 4: Create test data
test_df = pd.DataFrame({
    'feature1': np.random.randn(1000),
    'feature2': np.random.randn(1000)
})
test_dask = dd.from_pandas(test_df, npartitions=4)

# Step 5: Get predictions from all models
print("Making predictions...")
pred1 = model1.predict(test_dask).compute()
pred2 = model2.predict(test_dask).compute()
pred3 = model3.predict(test_dask).compute()

# Step 6: MERGE - Majority voting
predictions = np.array([pred1, pred2, pred3])
final_predictions = np.apply_along_axis(
    lambda x: np.bincount(x.astype(int)).argmax(),
    axis=0,
    arr=predictions
)

print(f"\nFinal predictions (first 10): {final_predictions[:10]}")
print(f"Prediction distribution: {np.bincount(final_predictions)}")

# Clean up
client.close()