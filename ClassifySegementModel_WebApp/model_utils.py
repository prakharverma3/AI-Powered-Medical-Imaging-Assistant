"""
model_utils.py
──────────────
All custom Keras layers and helper functions needed to deserialize
the saved BRISC-2025 model (SwinEfficientNet_v3).

Import this BEFORE calling tf.keras.models.load_model().
"""

import tensorflow as tf
from tensorflow.keras import layers, Model

# ── Version-safe registration decorator ──────────────────────────────────────
# tf.keras.saving.register_keras_serializable was added in TF 2.12 / Keras 2.12
# Older TF versions use tf.keras.utils.register_keras_serializable instead.
# We pick whichever is available so the file works on any TF version.
try:
    _register = tf.keras.saving.register_keras_serializable
except AttributeError:
    _register = tf.keras.utils.register_keras_serializable


# ══════════════════════════════════════════════════════
#  WINDOW ATTENTION
# ══════════════════════════════════════════════════════
@_register(package="brisc")
class WindowAttention(layers.Layer):
    """Window-based Multi-Head Self-Attention."""

    def __init__(self, dim, num_heads, **kwargs):
        super().__init__(**kwargs)
        self.dim       = dim
        self.num_heads = num_heads
        self.scale     = (dim // num_heads) ** -0.5
        self.qkv       = layers.Dense(dim * 3, use_bias=True)
        self.proj      = layers.Dense(dim)

    def call(self, x, training=False):
        B = tf.shape(x)[0]
        N = tf.shape(x)[1]
        C = self.dim

        qkv = self.qkv(x)
        qkv = tf.reshape(qkv, [B, N, 3, self.num_heads, C // self.num_heads])
        qkv = tf.transpose(qkv, [2, 0, 3, 1, 4])
        q, k, v = qkv[0], qkv[1], qkv[2]

        attn = tf.matmul(q, k, transpose_b=True) * self.scale
        attn = tf.nn.softmax(attn, axis=-1)

        x = tf.matmul(attn, v)
        x = tf.transpose(x, [0, 2, 1, 3])
        x = tf.reshape(x, [B, N, C])
        x = self.proj(x)
        return x

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"dim": self.dim, "num_heads": self.num_heads})
        return cfg


# ══════════════════════════════════════════════════════
#  SWIN BLOCK
# ══════════════════════════════════════════════════════
@_register(package="brisc")
class SwinBlock(layers.Layer):
    """One complete Swin Transformer block (Pre-LN variant)."""

    def __init__(self, dim, num_heads, mlp_ratio=4.0, dropout=0.1, **kwargs):
        super().__init__(**kwargs)
        self.dim       = dim
        self.num_heads = num_heads
        self.mlp_ratio = mlp_ratio
        self.dropout   = dropout

        self.norm1 = layers.LayerNormalization(epsilon=1e-6)
        self.attn  = WindowAttention(dim, num_heads)
        self.norm2 = layers.LayerNormalization(epsilon=1e-6)

        mlp_hidden = int(dim * mlp_ratio)
        self.mlp = tf.keras.Sequential([
            layers.Dense(mlp_hidden, activation="gelu"),
            layers.Dropout(dropout),
            layers.Dense(dim),
            layers.Dropout(dropout),
        ])

    def call(self, x, training=False):
        B = tf.shape(x)[0]
        H = x.shape[1]
        W = x.shape[2]
        C = self.dim

        shortcut = x
        x        = self.norm1(x)
        x_flat   = tf.reshape(x, [B, H * W, C])
        attn_out = self.attn(x_flat, training=training)
        attn_out = tf.reshape(attn_out, [B, H, W, C])
        x        = shortcut + attn_out
        x        = x + self.mlp(self.norm2(x), training=training)
        return x

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            "dim":       self.dim,
            "num_heads": self.num_heads,
            "mlp_ratio": self.mlp_ratio,
            "dropout":   self.dropout,
        })
        return cfg


# ══════════════════════════════════════════════════════
#  CUSTOM OBJECTS DICT  (pass to load_model)
# ══════════════════════════════════════════════════════
CUSTOM_OBJECTS = {
    "WindowAttention": WindowAttention,
    "SwinBlock":       SwinBlock,
}