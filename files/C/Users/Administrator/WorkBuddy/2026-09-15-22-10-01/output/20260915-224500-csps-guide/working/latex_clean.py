# -*- coding: utf-8 -*-
"""Convert LaTeX / KaTeX source into readable plain text for DOCX output."""
import re

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "θ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ",
    "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}

SYMBOLS = {
    # set / logic
    "cup": "∪", "cap": "∩", "setminus": "∖", "subseteq": "⊆", "supseteq": "⊇",
    "subset": "⊂", "supset": "⊃", "subsetneq": "⊊", "supsetneq": "⊋",
    "in": "∈", "notin": "∉", "ni": "∋", "emptyset": "∅", "varnothing": "∅",
    "forall": "∀", "exists": "∃", "nexists": "∄", "neg": "¬", "lnot": "¬",
    "land": "∧", "wedge": "∧", "lor": "∨", "vee": "∨", "oplus": "⊕",
    "otimes": "⊗", "odot": "⊙", "perp": "⊥",
    # arrows / relations
    "to": "→", "rightarrow": "→", "Rightarrow": "⇒", "longrightarrow": "⟶",
    "longmapsto": "⟼", "mapsto": "↦", "leftarrow": "←", "Leftarrow": "⇐",
    "leftrightarrow": "↔", "Leftrightarrow": "⇔", "uparrow": "↑", "downarrow": "↓",
    "le": "≤", "leq": "≤", "leqslant": "≤", "ge": "≥", "geq": "≥", "geqslant": "≥",
    "neq": "≠", "ne": "≠", "approx": "≈", "equiv": "≡", "sim": "∼",
    "simeq": "≃", "cong": "≅", "propto": "∝", "ll": "≪", "gg": "≫",
    "prec": "≺", "succ": "≻", "preceq": "⪯", "succeq": "⪰",
    # operators
    "times": "×", "div": "÷", "cdot": "·", "pm": "±", "mp": "∓", "ast": "∗",
    "circ": "∘", "bullet": "∙", "star": "⋆", "sum": "∑", "prod": "∏",
    "coprod": "∐", "int": "∫", "iint": "∬", "oint": "∮", "partial": "∂",
    "nabla": "∇", "prime": "′", "angle": "∠", "triangle": "△",
    "infty": "∞", "aleph": "ℵ", "hbar": "ℏ", "ell": "ℓ",
    "ldots": "…", "cdots": "⋯", "vdots": "⋮", "ddots": "⋱", "dots": "…",
    "lfloor": "⌊", "rfloor": "⌋", "lceil": "⌈", "rceil": "⌉",
    "langle": "⟨", "rangle": "⟩", "mid": "∣", "nmid": "∤",     "parallel": "∥",
    "gets": "←", "leftarrow": "←",
}

# commands whose argument must be dropped (spacing / style only)
DROP_ARG = ("mathbf", "mathrm", "mathit", "mathsf", "mathtt", "boldsymbol",
            "bm", "mathcal", "mathscr", "frak", "hat", "vec", "tilde",
            "bar", "dot", "ddot", "check", "breve", "acute", "grave",
            "operatorname*")

FUNCTIONS = ("gcd", "lcm", "max", "min", "log", "ln", "lg", "exp", "sin",
             "cos", "tan", "cot", "arcsin", "arccos", "arctan", "sec", "csc",
             "lim", "sup", "inf", "arg", "deg", "dim", "ker", "hom", "Pr")

SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
       "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻",
       "n": "ⁿ", "i": "ⁱ", "T": "ᵀ", "(": "⁽", ")": "⁾"}
SUB = {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅",
       "6": "₆", "7": "₇", "8": "₈", "9": "₉", "+": "₊", "-": "₋",
       "i": "ᵢ", "j": "ⱼ", "n": "ₙ", "a": "ₐ", "e": "ₑ", "o": "ₒ",
       "x": "ₓ", "k": "ₖ", "t": "ₜ", "s": "ₛ", "p": "ₚ", "r": "ᵣ"}

ENV_ROW_SPLIT = re.compile(r"\\\\")
ENV_RE = re.compile(r"\\begin\{([a-zA-Z*]+)\}(.*?)\\end\{\1\}", re.S)


def _take_arg(s, i):
    """Return (arg, next_index) for a {...} group starting at/after i."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s) or s[i] != "{":
        m = re.match(r"\\?[a-zA-Z0-9]", s[i:i + 2])
        return (m.group(0) if m else ""), (i + (1 if not m else len(m.group(0))))
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def _to_sup(t):
    if len(t) == 1 and t in SUP:
        return SUP[t]
    if t and all(c in SUP for c in t):
        return "".join(SUP[c] for c in t)
    return "^(" + t + ")"


def _to_sub(t):
    if len(t) == 1 and t in SUB:
        return SUB[t]
    if t and all(c in SUB for c in t):
        return "".join(SUB[c] for c in t)
    return "_(" + t + ")"


def _convert(text):
    s = text

    # --- environments: aligned / array / cases / matrices -> readable lines
    def env_sub(m):
        env, inner = m.group(1), m.group(2)
        # drop column spec of array/tabular: {ll} {|c|c|} {lcr}
        inner = re.sub(r"^\s*\{?[lcr|:\s]{1,12}\}?", "", inner)
        inner = re.sub(r"\\hspace\{[^}]*\}", " ", inner)
        rows = ENV_ROW_SPLIT.split(inner)
        lines = []
        for r in rows:
            r = r.replace("&", "  ")
            r = r.replace("\\hline", "").strip()
            if r:
                lines.append(r)
        return "\n".join(lines)

    prev = None
    while prev != s:
        prev = s
        s = ENV_RE.sub(env_sub, s)
    # strip leftover \begin{...} / \end{...}
    s = re.sub(r"\\(begin|end)\{[a-zA-Z*]+\}", "", s)

    # --- fractions, roots, binom, text-like wrappers
    for cmd in ("dfrac", "tfrac", "frac", "binom", "dbinom", "cfrac"):
        pat = re.compile(r"\\" + cmd + r"(?=\s*[{}\\a-zA-Z0-9])")
        while True:
            m = pat.search(s)
            if not m:
                break
            a, i1 = _take_arg(s, m.end())
            b, i2 = _take_arg(s, i1)
            rep = "(%s)/(%s)" % (a, b) if cmd in ("frac", "dfrac", "tfrac", "cfrac") \
                else "C(%s,%s)" % (a, b)
            s = s[:m.start()] + rep + s[i2:]

    # sqrt / root
    pat = re.compile(r"\\sqrt\s*\[([^\]]*)\]")
    s = pat.sub(lambda m: "^(1/(%s))" % m.group(1), s)
    pat = re.compile(r"\\sqrt(?=\s*[{}\\a-zA-Z0-9])")
    while True:
        m = pat.search(s)
        if not m:
            break
        a, i1 = _take_arg(s, m.end())
        s = s[:m.start()] + "√(%s)" % a + s[i1:]

    # text / operator wrappers -> keep inner content
    for cmd in ("text", "textbf", "textit", "textrm", "texttt", "mathrm",
                "operatorname", "mathbb", "mathcal", "underline") + DROP_ARG:
        pat = re.compile(r"\\" + cmd + r"\s*\{")
        while True:
            m = pat.search(s)
            if not m:
                break
            a, i1 = _take_arg(s, m.end() - 1)
            s = s[:m.start()] + a + s[i1:]

    # overline / bar variants -> combining overline on the content
    pat = re.compile(r"\\overline\s*\{")
    while True:
        m = pat.search(s)
        if not m:
            break
        a, i1 = _take_arg(s, m.end() - 1)
        s = s[:m.start()] + a + "̄" + s[i1:]

    # \pmod{n} / \bmod / \mod
    s = re.sub(r"\\pmod\s*\{([^}]*)\}", r" (mod \1)", s)
    s = re.sub(r"\\pmod\b", " mod ", s)
    s = re.sub(r"\\bmod\b", " mod ", s)
    s = re.sub(r"\\mod\b", " mod ", s)

    # --- big operators with limits: \sum_{i=1}^{n} -> sum(i=1..n)
    def op_limits(m):
        sym = {"sum": "∑", "prod": "∏", "coprod": "∐", "int": "∫",
               "iint": "∬", "oint": "∮", "bigcup": "⋃", "bigcap": "⋂",
               "lim": "lim", "max": "max", "min": "min"}.get(m.group(1), m.group(1))
        lo, hi = m.group(2), m.group(3)
        return "%s(%s ~ %s)" % (sym, lo, hi)

    s = re.sub(r"\\(sum|prod|coprod|int|iint|oint|bigcup|bigcap|lim|max|min)"
               r"\s*_\{([^{}]*)\}\s*\^\{([^{}]*)\}", op_limits, s)

    # --- symbol names (longest first, word boundary to avoid \gets/\left)
    for name in sorted(SYMBOLS, key=len, reverse=True):
        s = re.sub(r"\\" + re.escape(name) + r"(?![a-zA-Z])", SYMBOLS[name], s)
    for g, v in GREEK.items():
        s = re.sub(r"\\" + g + r"(?![a-zA-Z])", v, s)

    # function names without backslash-added braces
    for f in FUNCTIONS:
        s = re.sub(r"\\" + f + r"\b", f, s)

    # --- superscripts / subscripts
    def sub_sup(m):
        kind, arg = m.group(1), m.group(2)
        if arg.startswith("{") and arg.endswith("}"):
            arg = arg[1:-1]
        return _to_sup(arg) if kind == "^" else _to_sub(arg)

    s = re.sub(r"([\^_])\{([^{}]*)\}", sub_sup, s)
    s = re.sub(r"\^\s*([0-9a-zA-Z+\-T]{1})", lambda m: _to_sup(m.group(1)), s)
    s = re.sub(r"_\s*([0-9a-zA-Z+\-]{1})", lambda m: _to_sub(m.group(1)), s)

    # --- spacing / style-only commands
    s = re.sub(r"\\(left|right|big|Big|bigg|Bigg|displaystyle|textstyle|"
               r"scriptstyle|limits|nolimits|nonumber|notag|label|tag|"
               r"centering|small|large|footnotesize|normalsize|hfill)\b", "", s)
    s = re.sub(r"\\(quad|qquad|,|;|:|!| |hspace\{\d+\w*\})", " ", s)
    s = re.sub(r"\\(d?dot[s]?|hline|cline\{[^}]*\}|newline|\\)\s*", "\n", s)
    s = s.replace("\\$", "$").replace("\\%", "%").replace("\\&", "&")
    s = s.replace("\\#", "#").replace("\\_", "_").replace("\\{", "{").replace("\\}", "}")

    # --- unknown commands: keep the name without backslash
    s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)
    # stray backslashes left over from row separators (not C escapes like \0)
    s = re.sub(r"\\+(?=\s|$)", "", s)

    # --- drop leftover grouping braces and math delimiters
    s = s.replace("{", "").replace("}", "")
    s = s.replace("$", "")
    s = s.replace("&", " ")
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r" ?\n ?", "\n", s)
    return s.strip()


def latex_to_text(text):
    """Public entry: convert LaTeX (possibly mixed with Chinese) to readable text."""
    if not text:
        return ""
    # protect inline code spans already converted with backticks
    parts = re.split(r"(`[^`]*`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(p)
        else:
            out.append(_convert(p))
    return "".join(out)
