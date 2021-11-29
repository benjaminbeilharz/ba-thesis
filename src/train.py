import functools

import torch
import torch.nn as nn
import torch.optimizer as optim

import jax
import numpy as np
import optax

from .dtypes import *


class JAXTrainer:
    def __init__(self, net_init, loss_fn, optimizer: optax.GradientTransformation):
        self._net_init = net_init
        self._loss_fn = loss_fn
        self._opt = optimizer

    @functools.partial(jax.jit, static_argnums=0)
    def init(self, master_rng, data: Data):
        out_rng, init_rng = jax.random.split(master_rng)
        params = self._net_init(init_rng, data)
        opt_state = self._opt.init(params)
        out = {
            step: np.array(0),
            rng: out_rng,
            opt_state: opt_state,
            params: params
        }
        return out

    @functools.partial(jax.jit, static_argnums=0)
    def update(self, state: Mapping[str, Any], data: Data):
        rng, new_rng = jax.random.split(state['rng'])
        params = state['params']
        loss, grads = jax.value_and_grad(self._loss_fn)(params, rng, data)
        updates, opt_state = self._opt.update(g, state['opt_state'])
        params = optax.apply_updates(params, updates)

        new_state = {
            step: state['step'] + 1,
            rng: new_rng,
            opt_state: opt_state,
            params: params,
        }

        metrics = {
            step: state['step'],
            loss: loss,
        }

        return new_state, metrics


class TorchTrainer:
    def __init__(self, model: nn.Module, optimizer, data, cfg: dict):
        self.model = model(**cfg)
        self.optim = optimizer()
        self.data = data

    def train(self):
        self.model.train()
        pass

    def eval(self):
        self.model.eval()
        pass