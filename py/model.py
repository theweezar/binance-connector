import util
from trainer import preprocessing_data, print_predict_summary

X, y, symbol, time_steps = preprocessing_data()

latest_X = X[len(X) - (time_steps + 1) : len(X) - 1]

loaded_model = util.load_local_model(f"{symbol}_model.keras")

predict = loaded_model.predict(latest_X)

print(f"Time step: {time_steps}")
print_predict_summary(loaded_model, predict, None)
