from statistics import mean
from pprint import pp

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import metrics

# Regressors
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

from sklearn.cluster import KMeans

from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV


from tabulate import tabulate

metric_names = ["mean_absolute_error", "mean_squared_error", "max_error"]

def heatmap(df, size, title):
    plt.figure(figsize=size)
    sns.heatmap(df.corr(), annot=True).set(title=title)

def get_results(test, pred):
    mae = metrics.mean_absolute_error(test, pred)
    mse = metrics.mean_squared_error(test, pred)
    max_error = metrics.max_error(test, pred)

    return mae, mse, max_error

def get_best_model(model, input_train, target_train):
    if model is RandomForestRegressor:
        parameters = {
            "n_estimators": list(range(100, 1000, 100)),
            "criterion": ["squared_error", "absolute_error", "friedman_mse"],
            "max_depth": list(range(0, 100, 10)) + [None],
            "min_samples_split": list(range(2, 10)),
            "min_samples_leaf": list(range(0, 5)),
            "max_features": ["sqrt", "log2", None],
            "bootstrap": [True, False],
            "oob_score": [True, False],
            "random_state": 115
        }
    elif model is GradientBoostingRegressor:
        parameters = {
            "loss": ["squared_error", "absolute_error", "huber", "quantile"],
            "learning_rate": [0.01, 0.05, 0.1, 0.15, 0.2, 0.5],
            "n_estimators": list(range(100, 1000, 100)),
            "subsample": [0.6, 0.7, 0.8, 0.9, 1],
            "min_samples_split": list(range(1, 10)) + list(range(10, 100, 10)),
            "max_depth": list(range(1, 10)),
            "warm_start": [True, False],
            "criterion": ["friedman_mse", "squared_error"],
            "random_state": 115
        }
    elif model is DecisionTreeRegressor:
        parameters = {
            "criterion": ["squared_error", "absolute_error", "friedman_mse"],
            "max_depth": list(range(0, 100, 10)) + [None],
            "min_samples_split": list(range(2, 10)),
            "min_samples_leaf": list(range(0, 5)),
            "max_features": ["sqrt", "log2", None],
            "bootstrap": [True, False],
            "oob_score": [True, False],
            "random_state": 115
        }
    else:
        model = model.fit(input_train, target_train)
        return model

    best = GridSearchCV(model, parameters, cv=10, random_state=115, n_jobs=-1).fit(input_train, target_train)

    return best

def regress(df, input_f, target_f, get_models=False):
    input_df = df[input_f]
    target_df = df[target_f]

    input_train, input_test, target_train, target_test = train_test_split(input_df, target_df, shuffle=True)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(random_state=115),
        "Gradient Boosting": GradientBoostingRegressor(random_state=115),
        "Decision Tree": DecisionTreeRegressor(random_state=115)
    }
    
    ress = {}

    for name, model in models.items():
        regressor = get_best_model(model, input_train, target_train)
        target_pred = regressor.predict(input_test)
        ress[name] = get_results(target_test, target_pred)
        models[name] = model

    if get_models:
        return ress, models
    else:
        return ress

def print_regression_results(res):
    data = [(name,) + scores for name, scores in res.items()]
    print(tabulate(data, headers=["Regressore"] + metric_names))