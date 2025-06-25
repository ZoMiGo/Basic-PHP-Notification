# Simple Neural Network Examples

This folder contains standalone Python scripts demonstrating basic feedforward neural networks using only the Python standard library.

## XOR example

`neural_network.py` trains on the classic XOR problem. It has one hidden layer and runs for 20,000 iterations.

Run it with:

```bash
python3 python_nn/neural_network.py
```

## Trading example

`trading_nn.py` shows a tiny two-hidden-layer network that can react to TradingView webhooks. The network learns from dummy BUY/SELL/IGNORE examples based on RSI, MA gap and trend.

Training and displaying predictions:

```bash
python3 python_nn/trading_nn.py
```

Start the webhook server after training by adding `--serve`:

```bash
python3 python_nn/trading_nn.py --serve
```

The server listens on port 8000 and expects JSON payloads like:

```json
{"rsi": 65, "ma_gap": 0.01, "trend": 1}
```

It responds with `{"decision": "BUY"}`, `"SELL"` or `"IGNORE"`.

### Sending decisions to PHP

When starting the server you can pass `--notify-url` to POST each AI decision
to a PHP endpoint (e.g. `insert.php` in this project):

```bash
python3 python_nn/trading_nn.py --serve --notify-url "http://localhost/insert.php"
```

The POST body will contain `subject=AI+Decision` and `comment` with the
predicted action.

### Example Pine Script alert

`tradingview_webhook_example.pine` shows how to build a JSON payload in Pine
Script and send it via a TradingView alert. Configure the alert's webhook URL to
point to your running Python server (e.g. `http://server:8000`).
