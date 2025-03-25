import util
import modelUtils
import numpy as np
from colorama import Fore, Style
from keras.src.models.sequential import Sequential
from keras.src.layers import Bidirectional
from keras.src.layers.rnn.lstm import LSTM
from keras.src.layers.core.dense import Dense
from keras.src.layers.regularization.dropout import Dropout
from keras.src.callbacks.history import History
from keras.src.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def create_sequences(features, target, time_steps):
    X, y = [], []
    for i in range(len(features) - time_steps * 2):
        X.append(features[i : i + time_steps])
        y.append(target[i + time_steps])
    return np.array(X), np.array(y)


def preprocessing_data():
    csv = util.get_csv()
    data = csv["data_frame"]
    symbol = data["symbol"][0]

    # Raw X values
    features = data[
        [
            "close",
            # "price_change",
            # "volatility",
            "ema_trend",
            # "rsi_7",
            # "rsi_14",
            "rsi_6",
            "rsi_9",
            # "rsi_12",
            # "rsi_30",
            # "ema_34",
            # "ema_89",
            "macd",
            "macd_signal"
        ]
    ]

    # Binary classification -> Up/Down -> raw y values
    target = (data["type"] == "U").astype(int)

    # Scale features
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)
    time_steps = 30

    X, y = create_sequences(features_scaled, target.values, time_steps)

    return X, y, symbol, time_steps


def train_with_model_1(x, y):
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=False
    )

    # Build the LSTM model
    model = Sequential(
        [
            LSTM(
                64,
                return_sequences=True,
                input_shape=(X_train.shape[1], X_train.shape[2]),
            ),
            Dropout(0.2),
            LSTM(64),
            Dropout(0.2),
            Dense(1, activation="sigmoid"),  # Binary classification
        ]
    )

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    # Train the model
    history = model.fit(
        X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test)
    )

    return model, history


def train_with_model_2(x, y):
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=False
    )

    model = Sequential(
        [
            Bidirectional(
                LSTM(64, return_sequences=True),
                input_shape=(X_train.shape[1], X_train.shape[2]),
            ),
            Dropout(0.3),
            Bidirectional(LSTM(64)),
            Dropout(0.3),
            Dense(1, activation="sigmoid"),  # Binary classification
        ]
    )

    # model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    model.compile(
        optimizer=Adam(learning_rate=0.0005),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    # Train the model
    history = model.fit(
        X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test)
    )

    return model, history


def print_history(history):
    if type(history) is History:
        history_dict = history.history
        accuracy = history_dict.get("accuracy")
        loss = history_dict.get("loss")
        val_accuracy = history_dict.get("val_accuracy")
        val_loss = history_dict.get("val_loss")

        print(
            f"\n{Fore.YELLOW}argmax accuracy:{Style.RESET_ALL} {accuracy[np.argmax(accuracy)]}"
        )
        print(f"\n{Fore.YELLOW}argmax loss:{Style.RESET_ALL} {loss[np.argmax(loss)]}")
        print(
            f"\n{Fore.YELLOW}argmax val_accuracy:{Style.RESET_ALL} {val_accuracy[np.argmax(val_accuracy)]}"
        )
        print(
            f"\n{Fore.YELLOW}argmax val_loss:{Style.RESET_ALL} {val_loss[np.argmax(val_loss)]}"
        )


def print_predict_summary(model: Sequential, predict: np.ndarray, history):
    model.summary()

    predict_value = predict[np.argmax(predict)][0]

    print_history(history)

    # print(f"\n{Fore.GREEN}predict:{Style.RESET_ALL} {" ".join(map(str, predict))}")
    print(f"\n{Fore.GREEN}argmax predict:{Style.RESET_ALL} {predict_value}")
    print(
        f"\n{Fore.GREEN}predict direction:{Style.RESET_ALL} {"Up" if predict_value > 0.5 else "Down"}"
    )


if __name__ == "__main__":
    X, y, symbol, time_steps = preprocessing_data()

    model, history = train_with_model_2(X, y)

    print_history(history)

    modelUtils.save_model(model, f"{symbol}_model.keras")
