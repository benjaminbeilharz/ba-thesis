from functools import partial

import haiku as hk
import jax
import optax as O

from src_old.jax_playground.loss import lm_with_mask_loss_fn
from src_old.jax_playground.train import JAXTrainer
from src_old.jax_playground.transformer import build_transformer_forward_fn


# from src_old.utils import get_config

# TODO: Read yaml config here
# cfg = get_config(None)


def main():
    # TODO: load data here
    steps = None
    train_dataset, vocab_size = None, None

    # build fns
    forward_fn = build_transformer_forward_fn(vocab_size, d_model, num_heads, num_layers, dropout_rate)
    forward_fn = hk.transform(forward_fn)
    loss_fn = partial(lm_with_mask_loss_fn, forward_fn.apply, vocab_size)

    optimizer = O.chain(
        O.clip_by_global_norm(grad_clip_value),
        O.adam(learning_rate=learning_rate, b1=.9, b2=.99)
    )

    updater = JAXTrainer(forward_fn.init, loss_fn, optimizer)

    # init params
    rng = jax.random.PRNGKey(42)
    data = next(train_dataset)
    state = updater.init(rng, data)

    for step in range(steps):
        data = next(train_dataset)
        state, metrics = updater.update(state, data)
