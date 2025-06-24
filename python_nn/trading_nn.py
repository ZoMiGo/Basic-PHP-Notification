import json
import math
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import request, parse


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def dsigmoid(y):
    return y * (1 - y)


def softmax(xs):
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    s = sum(exps)
    return [e / s for e in exps]


class SimpleNN:
    def __init__(self, input_size, h1_size, h2_size, output_size, lr=0.1):
        self.lr = lr
        self.w1 = [[random.uniform(-1, 1) for _ in range(input_size)]
                   for _ in range(h1_size)]
        self.b1 = [0.0 for _ in range(h1_size)]

        self.w2 = [[random.uniform(-1, 1) for _ in range(h1_size)]
                   for _ in range(h2_size)]
        self.b2 = [0.0 for _ in range(h2_size)]

        self.w3 = [[random.uniform(-1, 1) for _ in range(h2_size)]
                   for _ in range(output_size)]
        self.b3 = [0.0 for _ in range(output_size)]

    def forward(self, x):
        h1 = [sigmoid(sum(w_i * x_i for w_i, x_i in zip(w, x)) + b)
              for w, b in zip(self.w1, self.b1)]
        h2 = [sigmoid(sum(w_i * h_i for w_i, h_i in zip(w, h1)) + b)
              for w, b in zip(self.w2, self.b2)]
        o_in = [sum(w_i * h_i for w_i, h_i in zip(w, h2)) + b
                for w, b in zip(self.w3, self.b3)]
        o_out = softmax(o_in)
        return h1, h2, o_out

    def train(self, data, epochs=1000):
        for _ in range(epochs):
            x, target_idx = random.choice(data)
            target = [0.0, 0.0, 0.0]
            target[target_idx] = 1.0

            h1, h2, o_out = self.forward(x)

            # output error
            delta_o = [o - t for o, t in zip(o_out, target)]

            # gradients for w3 and b3
            grad_w3 = [[self.lr * d * h for h in h2] for d in delta_o]
            grad_b3 = [self.lr * d for d in delta_o]

            # hidden layer 2 error
            delta_h2 = [dsigmoid(h2[i]) * sum(self.w3[k][i] * delta_o[k]
                                              for k in range(len(self.w3)))
                         for i in range(len(h2))]

            grad_w2 = [[self.lr * d * h for h in h1] for d in delta_h2]
            grad_b2 = [self.lr * d for d in delta_h2]

            # hidden layer 1 error
            delta_h1 = [dsigmoid(h1[i]) * sum(self.w2[k][i] * delta_h2[k]
                                              for k in range(len(self.w2)))
                         for i in range(len(h1))]
            grad_w1 = [[self.lr * d * x_i for x_i in x] for d in delta_h1]
            grad_b1 = [self.lr * d for d in delta_h1]

            # update weights
            for i in range(len(self.w3)):
                for j in range(len(self.w3[i])):
                    self.w3[i][j] -= grad_w3[i][j]
            for i in range(len(self.b3)):
                self.b3[i] -= grad_b3[i]

            for i in range(len(self.w2)):
                for j in range(len(self.w2[i])):
                    self.w2[i][j] -= grad_w2[i][j]
            for i in range(len(self.b2)):
                self.b2[i] -= grad_b2[i]

            for i in range(len(self.w1)):
                for j in range(len(self.w1[i])):
                    self.w1[i][j] -= grad_w1[i][j]
            for i in range(len(self.b1)):
                self.b1[i] -= grad_b1[i]

    def predict(self, x):
        _, _, o_out = self.forward(x)
        return int(max(range(len(o_out)), key=lambda i: o_out[i]))


# Dummy training data: [rsi_normalized, ma_gap, trend]
# trend: 1 = uptrend, -1 = downtrend, 0 = sideways
# labels: 0 = BUY, 1 = SELL, 2 = IGNORE
TRAIN_DATA = [
    ([0.2, 0.01, 1], 0),
    ([0.25, 0.02, 1], 0),
    ([0.8, -0.02, -1], 1),
    ([0.75, -0.03, -1], 1),
    ([0.5, 0.0, 0], 2),
    ([0.55, 0.0, 0], 2),
]


def build_and_train():
    nn = SimpleNN(input_size=3, h1_size=5, h2_size=5, output_size=3, lr=0.3)
    nn.train(TRAIN_DATA, epochs=5000)
    return nn


def run_server(nn, host="0.0.0.0", port=8000, notify_url=None):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            try:
                data = json.loads(body)
                rsi = float(data.get("rsi", 50)) / 100.0
                ma_gap = float(data.get("ma_gap", 0))
                trend = float(data.get("trend", 0))
                idx = nn.predict([rsi, ma_gap, trend])
                decision = ["BUY", "SELL", "IGNORE"][idx]

                if notify_url:
                    try:
                        payload = parse.urlencode({
                            "subject": "AI Decision",
                            "comment": decision
                        }).encode()
                        request.urlopen(notify_url, data=payload, timeout=5)
                    except Exception as notify_err:
                        print("Notify failed:", notify_err)

                resp = json.dumps({"decision": decision}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                msg = json.dumps({"error": str(e)}).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)

    server = HTTPServer((host, port), Handler)
    print(f"Serving on {host}:{port}")
    if notify_url:
        print(f"Notifications to {notify_url}")
    server.serve_forever()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Simple trading NN")
    parser.add_argument("--serve", action="store_true", help="start webhook server")
    parser.add_argument("--notify-url", help="optional URL to POST decisions to")
    args = parser.parse_args()

    nn = build_and_train()

    # show predictions for training data
    for features, label in TRAIN_DATA:
        pred = nn.predict(features)
        print(f"Input: {features} => Predicted: {pred} Target: {label}")

    if args.serve:
        run_server(nn, notify_url=args.notify_url)


if __name__ == "__main__":
    main()
