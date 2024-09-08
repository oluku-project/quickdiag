from celery import shared_task
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from django.utils import timezone
from pathlib import Path
import pickle5 as pickle
from .models import ActivityLog, TrainedModel
from django.conf import settings
import pandas as pd


# Import your activity log cleanup task
@shared_task
def delete_old_logs():
    retention_period = timezone.now() - timezone.timedelta(days=90)
    ActivityLog.objects.filter(timestamp__lt=retention_period).delete()


# Task to train the model
@shared_task
def train_model_task(model_type="RandomForest"):
    # Load data
    data = pd.read_csv(f"{settings.STATICFILES_DIRS[0]}/model/data.csv")
    data = data.drop(["Unnamed: 32", "id"], axis=1)
    data["diagnosis"] = data["diagnosis"].map({"M": 1, "B": 0})

    X = data.drop("diagnosis", axis=1)
    y = data["diagnosis"]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scaling data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Select model type
    if model_type == "NaiveBayes":
        model = GaussianNB()
    elif model_type == "SVM":
        model = SVC(probability=True)
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)

    # Train model
    model.fit(X_train_scaled, y_train)

    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Save model and scaler
    version = str(TrainedModel.objects.filter(name=model_type).count() + 1)
    model_dir = Path(f"{settings.STATICFILES_DIRS[0]}/model")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / f"{model_type}_v{version}.pkl"
    scaler_path = model_dir / f"{model_type}_scaler_v{version}.pkl"

    with open(model_path, "wb") as model_file:
        pickle.dump(model, model_file)
    with open(scaler_path, "wb") as scaler_file:
        pickle.dump(scaler, scaler_file)

    # Set previous models to non-default
    TrainedModel.objects.filter(is_default=True).update(is_default=False)

    # Save the trained model to the database
    TrainedModel.objects.create(
        name=model_type,
        version=version,
        model_type=model_type,
        accuracy=round(accuracy, 6),
        precision=round(precision, 6),
        recall=round(recall, 6),
        f1_score=round(f1, 6),
        training_data_path=str(model_dir / "data.csv"),
        model_file_path=str(model_path),
        scaler_file_path=str(scaler_path),
        is_default=True,
    )
