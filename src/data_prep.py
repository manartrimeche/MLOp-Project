# src/data_prep.py
import pathlib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_raw_data(path: str) -> pd.DataFrame:
    # Dataset avec séparateur ; et virgule pour décimales
    df = pd.read_csv(path, sep=';')
    # Supprimer colonnes entièrement vides
    df = df.dropna(axis=1, how='all')
    # Nettoyer les noms de colonnes
    df.columns = df.columns.str.strip()
    return df

def clean_and_prepare(df: pd.DataFrame):
    # Conversion des colonnes numériques (sauf Date, Time)
    colonnes_numeriques = [col for col in df.columns if col not in ['Date', 'Time']]
    for col in colonnes_numeriques:
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remplir les NaN numériques par la moyenne
    for col in df.select_dtypes(include='number').columns:
        df[col].fillna(df[col].mean(), inplace=True)

    # Option: normaliser quelques colonnes (si elles existent)
    colonnes_a_normaliser = [
        'Consommation', 'Température', 'Pression',
        'Humidité', 'VitesseVent', 'DirectionVent'
    ]
    colonnes_existantes = [c for c in colonnes_a_normaliser if c in df.columns]
    if colonnes_existantes:
        scaler = StandardScaler()
        df[colonnes_existantes] = scaler.fit_transform(df[colonnes_existantes])

    return df

def get_regression_splits(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    # Cible : NO2(GT)
    if 'NO2(GT)' not in df.columns:
        raise ValueError("La colonne cible 'NO2(GT)' est absente du dataset.")

    X = df.drop(columns=['NO2(GT)', 'Date', 'Time'], errors='ignore')
    y = df['NO2(GT)']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test

def load_regression_data():
    # Racine du projet = dossier MLOp-Project
    project_root = pathlib.Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "prédiction_de_la_qualité_de_air.csv"

    df = load_raw_data(data_path)
    df = clean_and_prepare(df)
    return get_regression_splits(df)