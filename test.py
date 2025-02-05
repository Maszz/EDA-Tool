import numpy as np
import polars as pl
import lightgbm as lgb
from boruta import BorutaPy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import lightgbm as lgb

# Generate synthetic dataset
np.random.seed(42)
num_samples = 200
num_features = 10

X = np.random.rand(num_samples, num_features)
y = np.random.rand(num_samples)

# Convert to Polars DataFrame (optional, BorutaPy expects numpy arrays)
df = pl.DataFrame(X, schema=[f"Feature_{i}" for i in range(num_features)])
df = df.with_columns(pl.Series("Target", y))

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Initialize BorutaPy Feature Selector
try:
    print("🔍 Testing BorutaPy feature selection...")

    # Use LightGBM or RandomForest as the base estimator
    base_model = RandomForestRegressor(n_jobs=-1, random_state=42)

    # Initialize Boruta feature selector
    boruta_selector = BorutaPy(
        base_model,
        n_estimators="auto",
        verbose=2,
        random_state=42,
    )

    # Fit Boruta
    boruta_selector.fit(X_train, y_train)

    # Print selected features
    selected_features = np.array([f"Feature_{i}" for i in range(num_features)])[
        boruta_selector.support_
    ]
    print(boruta_selector.support_)
    print("✅ BorutaPy Feature Selection Completed Successfully!")
    print("📌 Selected Features:", selected_features)

except Exception as e:
    print("❌ BorutaPy Test Failed!")
    print(f"Error: {e}")
