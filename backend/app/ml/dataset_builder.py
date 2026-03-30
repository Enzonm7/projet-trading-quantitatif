import pandas as pd
from feature_engineer import FeatureEngineer

class DatasetBuilder:
    
    def __init__(self, feature_engineer: FeatureEngineer, horizon: int = 5):
        self.feature_engineer = feature_engineer
        self.horizon = horizon

    def labelliser_convergence(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['zscore_futur'] = df['zscore'].shift(-self.horizon)
        df = df.dropna()
        df['target'] = (df['zscore_futur'].abs() < df['zscore'].abs()).astype(int)
        return df

    def splitter_temporel(self, df: pd.DataFrame) -> tuple:
        df = df.copy()
        train_idx = int(len(df) * 0.70)
        val_idx = int(len(df) * 0.85)
        df_train = df.iloc[:train_idx]
        df_val = df.iloc[train_idx:val_idx]
        df_test = df.iloc[val_idx:]
        return (df_train, df_val, df_test)

    def preparer_dataset(self, df: pd.DataFrame) -> tuple:
        df = df.copy()
        df = self.feature_engineer.create_ml_features(df)
        df = self.labelliser_convergence(df)
        df_train, df_val, df_test = self.splitter_temporel(df)
        return (df_train, df_val, df_test)