from django.core.management.base import BaseCommand
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd
import pickle5 as pickle
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from PaulVideoPlatform import settings
from pathlib import Path
from ml.models import TrainedModel
import os


def get_clean_data():
    data = pd.read_csv(f"{settings.STATICFILES_DIRS[0]}/model/data.csv")
    data = data.drop(["Unnamed: 32", "id"], axis=1)
    data["diagnosis"] = data["diagnosis"].map({"M": 1, "B": 0})
    return data


def create_model(data):
    X = data.drop("diagnosis", axis=1)
    y = data["diagnosis"]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Fit the scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    return model, scaler, accuracy, precision, recall, f1


class Command(BaseCommand):
    help = "Train and save a machine learning model with metadata"

    def handle(self, *args, **kwargs):
        # Clean the data
        data = get_clean_data()

        # Create the model and get metrics
        model, scaler, accuracy, precision, recall, f1 = create_model(data)

        # Create dynamic model name and version
        model_name = "breast_cancer_model"
        version = str(TrainedModel.objects.filter(name=model_name).count() + 1)

        # Paths for saving the model and scaler
        model_dir = Path(f"{settings.STATICFILES_DIRS[0]}/model")
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / f"{model_name}_v{version}.pkl"
        scaler_path = model_dir / f"{model_name}_scaler_v{version}.pkl"

        # Save the model and scaler
        with open(model_path, "wb") as model_file:
            pickle.dump(model, model_file)
        with open(scaler_path, "wb") as scaler_file:
            pickle.dump(scaler, scaler_file)

        # Set all previous models to non-default
        TrainedModel.objects.filter(is_default=True).update(is_default=False)

        # Create a record in the database
        TrainedModel.objects.create(
            name=model_name,
            version=version,
            model_type="RandomForestClassifier",
            accuracy=round(accuracy, 6),
            precision=round(precision, 6),
            recall=round(recall, 6),
            f1_score=round(f1, 6),
            training_data_path=model_dir / f"data.csv",
            model_file_path=str(model_path),
            scaler_file_path=str(scaler_path),
            is_default=True,
        )

        self.stdout.write(
            "\n_______________TRAINING BREAST CANCER DATASET MODEL__________________"
        )
        self.stdout.write(f"\t name:{model_name}")
        self.stdout.write(f"\t version:{version}")
        self.stdout.write(f"\t model_type: RandomForestClassifier")
        self.stdout.write(f"\t accuracy:{round(accuracy,6)}")
        self.stdout.write(f"\t precision:{round(precision, 6)}")
        self.stdout.write(f"\t recall:{round(recall, 6)}")
        self.stdout.write(f"\t f1_score:{round(f1, 6)}")
        self.stdout.write(f"\t training_data_path: {model_dir/'data.csv'}")
        self.stdout.write(f"\t model_file_path:{str(model_path)}")
        self.stdout.write(f"\t scaler_file_path:{str(scaler_path)}")
        self.stdout.write("_____________________________________________\n")
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully trained and saved model {model_name} v{version}"
            )
        )
