# -*- coding: utf-8 -*-
"""Replace glyphs that Chinese fonts (SimSun/WPS default) cannot render.

Fonts such as SimSun cover GB2312 math symbols (<=, >=, union, sigma, sqrt...)
but NOT most Unicode sub/superscript letters. Those show up as tofu boxes in
WPS and print as garbage. Sub/superscripts are therefore linearised
(a_1 -> a[1], x^2 -> x^2) and a few remaining oddities are replaced.
"""
import re

SUB = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
    "₆": "6", "₇": "7", "₈": "8", "₉": "9", "₊": "+", "₋": "-",
    "ₐ": "a", "ₑ": "e", "ₕ": "h", "ᵢ": "i", "ⱼ": "j", "ₖ": "k",
    "ₗ": "l", "ₘ": "m", "ₙ": "n", "ₒ": "o", "ₚ": "p", "ᵣ": "r",
    "ₛ": "s", "ₜ": "t", "ᵤ": "u", "ᵥ": "v", "ₓ": "x",
}
SUP = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁺": "+", "⁻": "-",
    "ⁿ": "n", "ⁱ": "i", "ᵀ": "T", "⁽": "(", "⁾": ")",
}
SINGLE = {
    "⋯": "...", "⋰": "...", "⋱": "...",
    "⊆": " 包含于 ", "⊇": " 包含 ", "⊂": " 真包含于 ", "⊃": " 真包含 ",
    "⊄": " 不包含于 ", "∈": " 属于 ", "∉": " 不属于 ",
    "∪": " 并 ", "∩": " 交 ", "∅": " 空集 ",
    "∀": " 任意 ", "∃": " 存在 ", "∄": " 不存在 ",
    "→": " -> ", "←": " <- ", "↔": " <-> ", "⇒": " => ", "⇐": " <= ",
    "⇔": " <=> ", "↦": " -> ", "⟶": " -> ", "⟼": " -> ",
    "≤": " <= ", "≥": " >= ", "≠": " != ", "≈": " ~ ", "≡": " == ",
    "≢": " != ", "≃": " ~ ", "≅": " ~ ", "∼": " ~ ",
    "×": " * ", "÷": " / ", "−": "-", "⋅": " * ", "∙": " * ",
    "∑": " sum ", "∏": " prod ", "∐": " coprod ", "∫": " int ",
    "√": " sqrt ", "∞": " INF ", "∠": " angle ",
    "∥": " || ", "⊥": " 垂直于 ", "⊕": " xor ", "⊗": " (x) ",
    "∧": " and ", "∨": " or ", "¬": " not ",
    "⌈": " ceil ", "⌉": " ", "⌊": " floor ", "⌋": " ",
    "′": "'", "″": "\"", "∂": " d ", "∇": " grad ",
    "\u00a0": " ", "\u200b": "", "\u200d": "",
    "∣": " | ", "∤": " 不整除 ", "≪": " << ", "≫": " >> ",
    "≺": " < ", "≻": " > ", "⪯": " <= ", "⪰": " >= ",
    # not covered by GB2312 -> missing glyph in SimSun / WPS
    "∖": " - ", "∘": " o ", "⋂": " 交 ", "⋃": " 并 ", "⋮": " ... ",
    "∗": " * ", "ℕ": "N", "ℤ": "Z", "ℚ": "Q", "ℝ": "R", "ℂ": "C",
    "⬇": " 下 ", "⬆": " 上 ", "ˈ": "'", "ɑ": "a", "ɛ": "e",
    "ː": ":", "ə": "e", "ʃ": "sh",
}
GREEK = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
    "ε": "epsilon", "ζ": "zeta", "η": "eta", "θ": "theta",
    "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu", "ν": "nu",
    "ξ": "xi", "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau",
    "υ": "upsilon", "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda",
    "Ξ": "Xi", "Π": "Pi", "Σ": "Sigma", "Φ": "Phi", "Ψ": "Psi",
    "Ω": "Omega",
}

SUB_RE = re.compile("[" + "".join(SUB) + "]+")
SUP_RE = re.compile("[" + "".join(SUP) + "]+")


def _sub(m):
    return "[" + "".join(SUB[c] for c in m.group(0)) + "]"


def _sup(m):
    body = "".join(SUP[c] for c in m.group(0))
    return "^" + body if len(body) == 1 else "^(" + body + ")"


def to_ascii_safe(text):
    if not text:
        return text
    # combining overline (set complement) -> ^c marker on the preceding token
    text = re.sub(r"(\S)\u0304", r"\1^c", text)
    text = text.replace("\u0304", "")
    text = SUB_RE.sub(_sub, text)
    text = SUP_RE.sub(_sup, text)
    for k, v in SINGLE.items():
        if k in text:
            text = text.replace(k, v)
    for k, v in GREEK.items():
        if k in text:
            text = text.replace(k, v)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text
