from django.core.management.base import BaseCommand
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd
import pickle5 as pickle
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from PaulVideoPlatform import settings
from pathlib import Path
from ml.models import TrainedModel
import os

from patients.utils import HelpResponse


def create_model(data, model_type):
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

    # Choose the model based on the model_type argument
    if model_type == "RandomForest":
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == "SVM":
        model = SVC(kernel="linear", probability=True, random_state=42)
    elif model_type == "NaiveBayes":
        model = GaussianNB()

    # Train the model
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

    def add_arguments(self, parser):
        # Adding the model_type argument
        parser.add_argument(
            "--model_type",
            type=str,
            default="RandomForest",  # Default model type is RandomForest
            choices=["RandomForest", "SVM", "NaiveBayes"],
            help="Specify the model type: RandomForest, SVM, or NaiveBayes.",
        )

    def handle(self, *args, **kwargs):
        model_type = kwargs["model_type"]  # Get the model type from the command line

        # Clean the data
        data = HelpResponse().get_clean_data()

        # Create the model and get metrics
        model, scaler, accuracy, precision, recall, f1 = create_model(data, model_type)

        # Create dynamic model name and version
        model_name = f"breast_cancer_model_{model_type.lower()}"
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
            model_type=model_type,
            accuracy=round(accuracy, 6),
            precision=round(precision, 6),
            recall=round(recall, 6),
            f1_score=round(f1, 6),
            training_data_path=model_dir / f"data.csv",
            model_file_path=str(model_path),
            scaler_file_path=str(scaler_path),
            is_default=True,
        )
        # Log the model details
        self.stdout.write(
            "\n_______________TRAINING BREAST CANCER DATASET MODEL__________________"
        )
        self.stdout.write(f"\t name: {model_name}")
        self.stdout.write(f"\t version: {version}")
        self.stdout.write(f"\t model_type: {model_type}")
        self.stdout.write(f"\t accuracy: {round(accuracy, 6)}")
        self.stdout.write(f"\t precision: {round(precision, 6)}")
        self.stdout.write(f"\t recall: {round(recall, 6)}")
        self.stdout.write(f"\t f1_score: {round(f1, 6)}")
        self.stdout.write(f"\t training_data_path: {model_dir / 'data.csv'}")
        self.stdout.write(f"\t model_file_path: {str(model_path)}")
        self.stdout.write(f"\t scaler_file_path: {str(scaler_path)}")
        self.stdout.write("_____________________________________________\n")
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully trained and saved model {model_name} v{version}"
            )
        )
