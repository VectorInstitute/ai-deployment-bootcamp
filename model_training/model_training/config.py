import pathlib
import model_training

PACKAGE_ROOT = pathlib.Path(model_training.__file__).resolve().parent.parent

print("Package root: ", PACKAGE_ROOT)

MODEL_PATH = PACKAGE_ROOT.parent / "models" / "diabetes_randomforest_pipeline" / "diabetes_randomforest_pipeline.pkl"

TRAINING_DATA_PATH = PACKAGE_ROOT.parent / "data" / "diabetes_012_health_indicators_BRFSS2015.csv"
SAMPLE_DATA_PATH = PACKAGE_ROOT.parent / "data" / "Diabetes_Indicators_sample" / "test_data.csv"

