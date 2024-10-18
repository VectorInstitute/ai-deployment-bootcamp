import pandas as pd 
import math

from sklearn.datasets import make_classification
from imblearn.under_sampling import NearMiss
from sklearn.metrics import classification_report, mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, accuracy_score

from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.decomposition import PCA

from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.preprocessing import FunctionTransformer

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import RandomForestClassifier
from model_training.preprocessing import TypeTransformer
from model_training.config import TRAINING_DATA_PATH, MODEL_PATH
import joblib


# ---- Load data
data = pd.read_csv(TRAINING_DATA_PATH , sep = "," , encoding = 'utf-8')

data['Diabetes_binary'] = data['Diabetes_012'].apply(lambda x: 0 if x==0 else 1)
data.drop(columns=['Diabetes_012'], inplace=True)

print('Data shape: ', data.shape)
print('No missing values:', data.isnull().sum())
print(f'Drop duplicates before shape: {data.shape}')
data.drop_duplicates(inplace = True)
print(f'Drop duplicates after shape: {data.shape}')

#:TODO Feature selection

#--------- Dealing with impalanced data  (slow)

print("Resampling for impalanced data... takes time ...")
X=data.drop(["Diabetes_binary"],axis=1)
Y=data["Diabetes_binary"]

nm = NearMiss(version=1, n_neighbors=5)
x_sm, y_sm = nm.fit_resample(X, Y)

# format back to a dataframe
x_sm = pd.DataFrame(x_sm, columns=X.columns)
y_sm = pd.Series(y_sm, name=Y.name)

print("Shape after resampling: ", y_sm.shape , x_sm.shape)
print("Y values count after resampling: ", y_sm.value_counts())


# ---- Build the model

print("Building RandomForest model")

rf_model = RandomForestClassifier(max_depth=10, n_estimators=100, random_state=42)

preprocessor = ColumnTransformer(
    transformers=[
        ('to_int', TypeTransformer(), make_column_selector(dtype_include="float")),
        ('num_impute', SimpleImputer(missing_values=pd.NA, strategy='mean'), make_column_selector(dtype_exclude="object")),
        ('num_scaler', StandardScaler(), make_column_selector(dtype_include="number"))
    ],
    remainder='passthrough'
)

# TODO: issue with pandas DF when stacking ColumnTransformers
# Step 2: Define a column transformer for encoding and scaling
encoding = ColumnTransformer(
    transformers=[
        ('num_scaler', StandardScaler(), make_column_selector(dtype_include="number"))
    ],
    remainder='passthrough'
)

# Step 3: Create the final pipeline
pipeline = make_pipeline(
    preprocessor,
    # encoding,
    rf_model
)

# ---- Train the model

X_train , X_test , Y_train , Y_test = train_test_split(x_sm,y_sm, test_size=0.3 , random_state=42)

print(f"Train shape: {X_train.shape}")
print(f"Test shape: {X_test.shape}")

pipeline.fit(X_train, Y_train)


# ------ evaluate the model

# make predictions on test set
y_pred = pipeline.predict(X_test)

print('Training set score: {:.4f}'.format(pipeline.score(X_train, Y_train)))
print('Test set score: {:.4f}'.format(pipeline.score(X_test, Y_test)))

#check MSE & RMSE 
mse = mean_squared_error(Y_test, y_pred)
print('Mean Squared Error : '+ str(mse))
rmse = mean_absolute_error(Y_test, y_pred)
print('Mean Absolute Error : '+ str(rmse))

matrix = classification_report(Y_train, Y_train)
print("Train:\n", matrix)

matrix = classification_report(Y_test, y_pred)
print("Test:\n", matrix)

#:TODO save confusion matrix
# calculating and plotting the confusion matrix
# cm1 = confusion_matrix(Y_test, y_pred)
# plot_confusion_matrix(conf_mat=cm1,show_absolute=True,
#                                 show_normed=True,
#                                 colorbar=True)

# ---- Save the model
joblib.dump(pipeline, MODEL_PATH)


# Check if Load the model works
pipeline = joblib.load(MODEL_PATH)