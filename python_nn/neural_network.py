import math
import random

# Simple feedforward neural network for XOR problem

# Define sigmoid activation and its derivative

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def dsigmoid(y):
    return y * (1 - y)


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, lr=0.5):
        self.lr = lr
        # Initialize weights with small random values
        self.w1 = [[random.uniform(-1, 1) for _ in range(input_size)]
                    for _ in range(hidden_size)]
        self.b1 = [random.uniform(-1, 1) for _ in range(hidden_size)]

        self.w2 = [[random.uniform(-1, 1) for _ in range(hidden_size)]
                    for _ in range(output_size)]
        self.b2 = [random.uniform(-1, 1) for _ in range(output_size)]

    def forward(self, x):
        # Hidden layer
        h_in = [sum(w_i * x_i for w_i, x_i in zip(w, x)) + b
                 for w, b in zip(self.w1, self.b1)]
        h_out = [sigmoid(h) for h in h_in]

        # Output layer
        o_in = [sum(w_i * h_i for w_i, h_i in zip(w, h_out)) + b
                 for w, b in zip(self.w2, self.b2)]
        o_out = [sigmoid(o) for o in o_in]
        return h_out, o_out

    def train(self, data, epochs=10000):
        for _ in range(epochs):
            x, target = random.choice(data)
            # Forward pass
            h_out, o_out = self.forward(x)

            # Calculate output error
            output_errors = [t - y for t, y in zip(target, o_out)]

            # Output layer gradients
            grad_w2 = [[self.lr * err * dsigmoid(y) * h
                        for h in h_out] for err, y in zip(output_errors, o_out)]
            grad_b2 = [self.lr * err * dsigmoid(y)
                        for err, y in zip(output_errors, o_out)]

            # Hidden layer error
            hidden_errors = [sum(err * w for err, w in zip(output_errors, col))
                              for col in zip(*self.w2)]

            # Hidden layer gradients
            grad_w1 = [[self.lr * h_err * dsigmoid(h_out_i) * x_i
                        for x_i in x]
                       for h_err, h_out_i in zip(hidden_errors, h_out)]
            grad_b1 = [self.lr * h_err * dsigmoid(h_out_i)
                        for h_err, h_out_i in zip(hidden_errors, h_out)]

            # Update weights and biases
            for i in range(len(self.w2)):
                for j in range(len(self.w2[i])):
                    self.w2[i][j] += grad_w2[i][j]
            for i in range(len(self.b2)):
                self.b2[i] += grad_b2[i]

            for i in range(len(self.w1)):
                for j in range(len(self.w1[i])):
                    self.w1[i][j] += grad_w1[i][j]
            for i in range(len(self.b1)):
                self.b1[i] += grad_b1[i]

    def predict(self, x):
        _, o_out = self.forward(x)
        return [1 if y > 0.5 else 0 for y in o_out]


def main():
    # XOR truth table
    data = [
        ([0, 0], [0]),
        ([0, 1], [1]),
        ([1, 0], [1]),
        ([1, 1], [0])
    ]

    nn = NeuralNetwork(input_size=2, hidden_size=4, output_size=1, lr=0.5)
    nn.train(data, epochs=20000)

    print("Trained weights:")
    print("W1:", nn.w1)
    print("b1:", nn.b1)
    print("W2:", nn.w2)
    print("b2:", nn.b2)

    for x, target in data:
        prediction = nn.predict(x)[0]
        print(f"Input: {x}, Predicted: {prediction}, Target: {target[0]}")


if __name__ == "__main__":
    main()
