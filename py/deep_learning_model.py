import util
import os
import numpy as np
from colorama import Fore, Style
from keras.src.models.sequential import Sequential
from keras.src.layers.rnn.lstm import LSTM
from keras.src.layers.core.dense import Dense
from keras.src.layers.regularization.dropout import Dropout
from keras.src.saving import load_model
from keras.src.callbacks.history import History
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

time_steps = 60
threshold = 0.5


def create_sequences(features, target, time_steps):
    X, y = [], []
    for i in range(len(features) - time_steps):
        X.append(features[i : i + time_steps])
        y.append(target[i + time_steps])
    return np.array(X), np.array(y)


def preprocessing_x_y_data():
    csv = util.get_csv()
    data = csv["data_frame"]

    # Raw X values
    features = data[
        [
            "Open",
            "High",
            "Low",
            "Close",
            # "Volume",
            "rsi_7",
            "rsi_14",
            "rsi_30",
            "ema_34",
            "ema_89",
        ]
    ]

    # Binary classification -> Up/Down -> raw y values
    target = (data["Type"] == "U").astype(int)

    # Scale features
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    X, y = create_sequences(features_scaled, target.values, time_steps)

    return X, y


def train_data(x, y):
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=False
    )

    # Build the LSTM model
    model = Sequential(
        [
            LSTM(
                50,
                return_sequences=True,
                input_shape=(X_train.shape[1], X_train.shape[2]),
            ),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1, activation="sigmoid"),  # Binary classification
        ]
    )

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    # Train the model
    history = model.fit(
        X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test)
    )

    return model, history


def print_predict_summary(predict: np.ndarray, history: History):
    # applied_threshold_predict = (predict > threshold).astype(int)
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

    predict_value = predict[np.argmax(predict)]

    # print(f"\n{Fore.GREEN}predict:{Style.RESET_ALL} {" ".join(map(str, predict))}")
    print(f"\n{Fore.GREEN}argmax predict:{Style.RESET_ALL} {predict_value}")
    print(
        f"\n{Fore.GREEN}predict direction:{Style.RESET_ALL} {"Up" if predict_value > 0.5 else "Down"}"
    )


X, y = preprocessing_x_y_data()

model, history = train_data(X, y)

# model_local_path = os.path.join(util.get_export_dir(), "model.keras")
# model.export(model_local_path)

predict = model.predict(X[len(X) - (time_steps + 1) : len(X) - 1])

print_predict_summary(predict, history)

# loaded_model = load_model(model_local_path)

# predict = loaded_model.predict(X[len(X) - (time_steps + 1):len(X) - 1])

# print_predict_summary(predict)
