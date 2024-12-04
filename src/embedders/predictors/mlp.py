import torch
import torch.nn as nn


class MLP(nn.Module):
    def __init__(
        self, pm, input_dim=0, hidden_dims=None, output_dim=0, tangent=True, task="classification", activation=nn.ReLU
    ):
        super().__init__()
        self.pm = pm  # Not used in the basic implementation
        self.task = task

        # Build architecture
        if hidden_dims is None:
            hidden_dims = []

        dimensions = [input_dim] + hidden_dims + [output_dim]
        layers = []

        # Create layers
        for i in range(len(dimensions) - 1):
            # bias = True if tangent or i > 0 else False  # First layer for non-tangent = no bias
            bias = not tangent and i == 0
            layers.append(nn.Linear(dimensions[i], dimensions[i + 1], bias=bias))

            # Add activation function after all layers except the last one
            if i < len(dimensions) - 2:
                layers.append(activation())

        # Register layers as a ModuleList
        self.layers = nn.ModuleList(layers)

    def forward(self, x):
        """Forward pass through the network."""
        for layer in self.layers:
            x = layer(x)
        return x

    def fit(self, X, y, epochs=1_000, lr=1e-2, batch_size=32):
        """Train the model."""
        opt = torch.optim.Adam(self.parameters(), lr=lr)
        if self.task == "classification":
            loss_fn = nn.CrossEntropyLoss()
            y = y.long()
        else:
            loss_fn = nn.MSELoss()
            y = y.float()

        self.train()
        for i in range(epochs):
            # for j in range(0, len(X), batch_size):
            #     X_batch = X[j : j + batch_size]
            #     y_batch = y[j : j + batch_size]

            #     opt.zero_grad()
            #     y_pred = self(X_batch)
            #     loss = loss_fn(y_pred, y_batch)
            #     loss.backward()
            #     opt.step()
            opt.zero_grad()
            y_pred = self(X)
            loss = loss_fn(y_pred, y)
            loss.backward()
            opt.step()

    def predict(self, X):
        """Make predictions."""
        self.eval()
        with torch.no_grad():
            if self.task == "classification":
                return self(X).argmax(1).detach()
            else:
                return self(X).detach()
