import util
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def preprocessing_data():
    csv = util.get_csv()
    data = csv["data_frame"]
    symbol = data["symbol"][0]
    data.dropna(inplace=True)

    # Raw X values
    x_features = data[
        [
            "close",
            "ema_trend",
            "rsi_6",
            "rsi_9",
            "ema_34",
            "ema_89",
            "macd",
            "macd_signal",
            "adx_14"
        ]
    ]

    # Binary classification -> Up/Down -> raw y values
    y_target = (data["type"] == "U").astype(int)

    return x_features, y_target, symbol


def train(x, y):
    # Split into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=False
    )

    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Logistic Regression model
    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)

    # Make predictions
    y_pred = model.predict(X_test_scaled)

    print(y_pred)

    # Model Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")

    # Classification Report
    print("Classification Report:\n", classification_report(y_test, y_pred))


if __name__ == "__main__":
    X, y, symbol = preprocessing_data()

    train(X, y)
