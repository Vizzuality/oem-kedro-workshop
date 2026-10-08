import logging

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


def _features(pixels: pd.DataFrame) -> pd.DataFrame:
    return pixels.filter(regex=r"^d\d+$")


def split_data(pixels: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split by site, not by pixel.

    Neighbouring pixels are almost identical, so a pixel-level split would put
    the same site in train and test and inflate the scores.
    """
    sites = pixels[["site_id", "label"]].drop_duplicates()
    train_sites, _ = train_test_split(
        sites["site_id"],
        test_size=params["test_size"],
        stratify=sites["label"],
        random_state=params["seed"],
    )
    is_train = pixels["site_id"].isin(train_sites)
    return pixels[is_train], pixels[~is_train]


def train_model(train: pd.DataFrame, params: dict) -> Pipeline:
    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        class_weight="balanced",
        random_state=params["seed"],
        n_jobs=-1,
    )
    return model.fit(_features(train), train["label"])


def evaluate_model(model: Pipeline, test: pd.DataFrame) -> dict:
    predicted = model.predict(_features(test))
    logger.info("\n%s", classification_report(test["label"], predicted))
    return classification_report(
        test["label"],
        predicted,
        target_names=["no_construction", "construction"],
        output_dict=True,
    )
