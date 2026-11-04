# -*- coding: utf-8 -*-
from latex_clean import latex_to_text

CASES = [
    r"\begin{aligned} 2g(k) &\le w(a_1,d_1) + w(b_{k+1},c_{k+1}) \\ &= g(k-1) + g(k+1). \end{aligned}",
    r"\begin{array}{ll} 1 &  \textbf{Input. } \text{The edges of the graph } e , \text{ where each element in } e \text{ is } (u, v, w) \\ 2 &  \textbf{Output. } result \\ 3 &  result \gets \varnothing \end{array}",
    r"\sum_{i=1}^{n} a_i \le n \cdot \max_{1 \le j \le k} b_j",
    r"\frac{a}{b} + \sqrt{x^2 + y^2} \ge \frac{2ab}{a+b}, \quad \gcd(a,b)=d",
    r"d_1[j] \le r - i + 1, \quad f(i) = \begin{cases} 1 & i = 0 \\ i \cdot f(i-1) & i > 0 \end{cases}",
    r"a \equiv b \pmod{p}, \quad \varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)",
    r"O(n \log n) 预处理， O(\log n) 查询， n \le 2 \times 10^5 ， T \le 10^4 。",
    r"\overline{A \cup B} = \overline{A} \cap \overline{B}",
    r"f_{i, j} = \min_{k < j} \{ f_{i-1, k} + w(k+1, j) \}",
]

for t in CASES:
    print("IN :", t)
    print("OUT:", latex_to_text(t))
    print("-" * 60)
