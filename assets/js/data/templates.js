/* ==========================================================================
   模板库：48 个竞赛模板，标注大纲等级、复杂度与易错点
   ========================================================================== */

window.TEMPLATES = [
  /* ---------------- 基础技巧 ---------------- */
  { n: "快读", c: "基础", lv: 3, cx: "O(n)",
    code: `inline int read(){
    int x = 0, f = 1; char c = getchar();
    while (!isdigit(c)) { if (c == '-') f = -1; c = getchar(); }
    while (isdigit(c))  { x = x * 10 + c - '0'; c = getchar(); }
    return x * f;
}`,
    note: "读入 10^6 级数据时比 cin 快 5–8 倍。注意 c 必须是 int 才能正确判 EOF。" },

  { n: "离散化", c: "基础", lv: 6, cx: "O(n log n)",
    code: `for (int i = 1; i <= n; i++) b[i] = a[i];
sort(b + 1, b + n + 1);
int m = unique(b + 1, b + n + 1) - b - 1;
for (int i = 1; i <= n; i++)
    a[i] = lower_bound(b + 1, b + m + 1, a[i]) - b;`,
    note: "值域 10^9 但只有 10^5 个数时的必备步骤。离散化后仍保持原序关系。" },

  { n: "二分查找（找左界）", c: "基础", lv: 4, cx: "O(log n)",
    code: `int l = 1, r = n, ans = -1;
while (l <= r) {
    int mid = (l + r) >> 1;
    if (a[mid] >= x) { ans = mid; r = mid - 1; }
    else l = mid + 1;
}`,
    note: "找第一个 ≥ x 的位置。若求右界把条件改为 a[mid] <= x 并令 l = mid + 1。" },

  { n: "二分答案（最大化）", c: "基础", lv: 4, cx: "O(n log V)",
    code: `int l = 0, r = 1e9;
while (l < r) {
    int mid = (l + r + 1) >> 1;
    if (check(mid)) l = mid;
    else r = mid - 1;
}
// 最小化写法：mid = (l+r)>>1; if(check(mid)) r = mid; else l = mid+1;`,
    note: "最容易死循环的地方：最大化必须 +1 上取整，最小化必须下取整，二者不可混用。" },

  { n: "一维前缀和 / 差分", c: "基础", lv: 3, cx: "O(n)",
    code: `// 前缀和
for (int i = 1; i <= n; i++) s[i] = s[i-1] + a[i];
// 查询 [l,r]
int sum = s[r] - s[l-1];

// 差分：区间 [l,r] 加 v
d[l] += v; d[r+1] -= v;
// 还原
for (int i = 1; i <= n; i++) d[i] += d[i-1];`,
    note: "2025 大纲把前缀和、差分明确列为 J 级新增考点，属于必拿分项。" },

  { n: "二维前缀和", c: "基础", lv: 4, cx: "O(1) 查询",
    code: `s[i][j] = s[i-1][j] + s[i][j-1] - s[i-1][j-1] + a[i][j];
// 子矩阵 (x1,y1)-(x2,y2)
int sum = s[x2][y2] - s[x1-1][y2] - s[x2][y1-1] + s[x1-1][y1-1];`,
    note: "容斥的几何直觉：加两次减一次，容易漏掉 -s[i-1][j-1]。" },

  { n: "高精度加法", c: "基础", lv: 4, cx: "O(n)",
    code: `string add(string a, string b) {
    reverse(a.begin(), a.end()); reverse(b.begin(), b.end());
    string c; int t = 0;
    for (int i = 0; i < (int)max(a.size(), b.size()) || t; i++) {
        if (i < (int)a.size()) t += a[i] - '0';
        if (i < (int)b.size()) t += b[i] - '0';
        c += char(t % 10 + '0'); t /= 10;
    }
    reverse(c.begin(), c.end());
    return c;
}`,
    note: "循环条件里的 || t 是关键，否则最高位进位会丢。" },

  { n: "对拍脚本", c: "基础", lv: 4, cx: "—",
    code: `@echo off
:loop
gen.exe > in.txt
std.exe < in.txt > out1.txt
my.exe  < in.txt > out2.txt
fc out1.txt out2.txt > nul
if not errorlevel 1 goto loop
echo WA!
pause`,
    note: "考场以外的第二生命。写完任何一题，先对拍 1000 组再提交。" },

  /* ---------------- 数据结构 ---------------- */
  { n: "并查集", c: "数据结构", lv: 6, cx: "近 O(1)",
    code: `int fa[N];
int find(int x) { return fa[x] == x ? x : fa[x] = find(fa[x]); }
void merge(int x, int y) { fa[find(x)] = find(y); }
// 初始化
for (int i = 1; i <= n; i++) fa[i] = i;`,
    note: "路径压缩 + 按秩合并才达到反阿克曼函数级。只写路径压缩在极端数据下可能被卡。" },

  { n: "带权并查集", c: "数据结构", lv: 7, cx: "近 O(1)",
    code: `int fa[N], w[N];   // w[x]: x 到父节点的权值
int find(int x) {
    if (fa[x] == x) return x;
    int r = find(fa[x]);
    w[x] += w[fa[x]];      // 先累积到根的距离
    return fa[x] = r;
}
// 合并 x,y 且 x 比 y 大 d：merge 时 w[fx] = w[y] + d - w[x]`,
    note: "关键顺序：必须先递归 find 再累加 w[x]，否则父节点的 w 还没更新。" },

  { n: "树状数组（单点改区间查）", c: "数据结构", lv: 6, cx: "O(log n)",
    code: `int c[N];
void add(int x, int v) { for (; x <= n; x += x & -x) c[x] += v; }
int sum(int x) { int s = 0; for (; x; x -= x & -x) s += c[x]; return s; }
// 区间 [l,r] 和：sum(r) - sum(l-1)`,
    note: "lowbit 的本质是「管辖范围」。求逆序对时先离散化再倒序插入。" },

  { n: "树状数组（区间改单点查）", c: "数据结构", lv: 6, cx: "O(log n)",
    code: `// 用差分数组建树状数组
void range_add(int l, int r, int v) { add(l, v); add(r + 1, -v); }
int point_query(int x) { return sum(x); }`,
    note: "区间修改 + 区间查询需要维护两个树状数组，属于常考的进阶变形。" },

  { n: "线段树（区间加 / 区间和）", c: "数据结构", lv: 6, cx: "O(log n)",
    code: `int tr[N << 2], lz[N << 2];
void pushup(int p) { tr[p] = tr[p<<1] + tr[p<<1|1]; }
void build(int p, int l, int r) {
    if (l == r) { tr[p] = a[l]; return; }
    int m = (l + r) >> 1;
    build(p<<1, l, m); build(p<<1|1, m+1, r); pushup(p);
}
void apply(int p, int l, int r, int v) { tr[p] += v * (r - l + 1); lz[p] += v; }
void pushdown(int p, int l, int r) {
    int m = (l + r) >> 1;
    apply(p<<1, l, m, lz[p]); apply(p<<1|1, m+1, r, lz[p]); lz[p] = 0;
}
void upd(int p, int l, int r, int ql, int qr, int v) {
    if (ql <= l && r <= qr) { apply(p, l, r, v); return; }
    pushdown(p, l, r); int m = (l + r) >> 1;
    if (ql <= m) upd(p<<1, l, m, ql, qr, v);
    if (qr > m)  upd(p<<1|1, m+1, r, ql, qr, v);
    pushup(p);
}
int qry(int p, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return tr[p];
    pushdown(p, l, r); int m = (l + r) >> 1, s = 0;
    if (ql <= m) s += qry(p<<1, l, m, ql, qr);
    if (qr > m)  s += qry(p<<1|1, m+1, r, ql, qr);
    return s;
}`,
    note: "数组开 4 倍。pushdown 必须在递归子区间之前调用，这是最常见的 WA 来源。" },

  { n: "ST 表（静态 RMQ）", c: "数据结构", lv: 6, cx: "O(1) 查询",
    code: `int st[20][N], lg[N];
void init() {
    lg[1] = 0;
    for (int i = 2; i <= n; i++) lg[i] = lg[i >> 1] + 1;
    for (int i = 1; i <= n; i++) st[0][i] = a[i];
    for (int k = 1; (1 << k) <= n; k++)
        for (int i = 1; i + (1 << k) - 1 <= n; i++)
            st[k][i] = max(st[k-1][i], st[k-1][i + (1 << (k-1))]);
}
int qry(int l, int r) {
    int k = lg[r - l + 1];
    return max(st[k][l], st[k][r - (1 << k) + 1]);
}`,
    note: "只支持静态查询。两个区间可以重叠，这是它能 O(1) 的原因。" },

  { n: "单调队列（滑动窗口最值）", c: "数据结构", lv: 5, cx: "O(n)",
    code: `int q[N], h = 1, t = 0;
for (int i = 1; i <= n; i++) {
    while (h <= t && q[h] <= i - k) h++;          // 弹出过期
    while (h <= t && a[q[t]] <= a[i]) t--;        // 维护单调
    q[++t] = i;
    if (i >= k) printf("%d ", a[q[h]]);
}`,
    note: "两个 while 的顺序不能换。求最小值把比较符反过来。" },

  { n: "单调栈（下一个更大元素）", c: "数据结构", lv: 5, cx: "O(n)",
    code: `stack<int> s;
for (int i = n; i >= 1; i--) {
    while (!s.empty() && a[s.top()] <= a[i]) s.pop();
    ans[i] = s.empty() ? 0 : s.top();
    s.push(i);
}`,
    note: "倒序扫描求右侧第一个更大值，正序扫描求左侧。栈里存下标而非值。" },

  { n: "字典树 Trie", c: "数据结构", lv: 6, cx: "O(L)",
    code: `int ch[N][26], cnt[N], tot;
void insert(char *s) {
    int p = 0;
    for (int i = 0; s[i]; i++) {
        int c = s[i] - 'a';
        if (!ch[p][c]) ch[p][c] = ++tot;
        p = ch[p][c];
    }
    cnt[p]++;
}
bool query(char *s) {
    int p = 0;
    for (int i = 0; s[i]; i++) {
        int c = s[i] - 'a';
        if (!ch[p][c]) return false;
        p = ch[p][c];
    }
    return cnt[p] > 0;
}`,
    note: "N 要开到 总字符数 × 1，不是单词数。01-Trie 可求最大异或对。" },

  { n: "对顶堆（动态中位数）", c: "数据结构", lv: 6, cx: "O(log n)",
    code: `priority_queue<int> big;                              // 大根堆，存较小的一半
priority_queue<int, vector<int>, greater<int>> small;  // 小根堆，存较大的一半
void add(int x) {
    if (big.empty() || x <= big.top()) big.push(x);
    else small.push(x);
    if (big.size() > small.size() + 1) { small.push(big.top()); big.pop(); }
    if (small.size() > big.size())     { big.push(small.top()); small.pop(); }
}
int median() { return big.top(); }`,
    note: "两个堆大小差不超过 1，中位数永远在堆顶。插入顺序影响平衡调整次数。" },

  { n: "Treap（分裂 / 合并）", c: "数据结构", lv: 8, cx: "期望 O(log n)",
    code: `int ls[N], rs[N], val[N], pri[N], sz[N], tot;
void pushup(int p) { sz[p] = sz[ls[p]] + sz[rs[p]] + 1; }
void split(int p, int v, int &x, int &y) {   // x: <=v, y: >v
    if (!p) { x = y = 0; return; }
    if (val[p] <= v) { x = p; split(rs[p], v, rs[p], y); }
    else             { y = p; split(ls[p], v, x, ls[p]); }
    pushup(p);
}
int merge(int x, int y) {
    if (!x || !y) return x | y;
    if (pri[x] < pri[y]) { rs[x] = merge(rs[x], y); pushup(x); return x; }
    else                 { ls[y] = merge(x, ls[y]); pushup(y); return y; }
}`,
    note: "分裂合并版比旋转版短且不易错。pri 用 rand() 即可，但建议手写 xorshift 提速。" },

  { n: "树链剖分", c: "数据结构", lv: 8, cx: "O(log² n)",
    code: `void dfs1(int u, int f) {
    fa[u] = f; dep[u] = dep[f] + 1; sz[u] = 1;
    for (int v : g[u]) if (v != f) {
        dfs1(v, u); sz[u] += sz[v];
        if (sz[v] > sz[son[u]]) son[u] = v;
    }
}
void dfs2(int u, int t) {
    top[u] = t; id[u] = ++cnt; rk[cnt] = u;
    if (son[u]) dfs2(son[u], t);
    for (int v : g[u]) if (v != fa[u] && v != son[u]) dfs2(v, v);
}
void path_add(int u, int v, int k) {
    while (top[u] != top[v]) {
        if (dep[top[u]] < dep[top[v]]) swap(u, v);
        upd(1, 1, n, id[top[u]], id[u], k);
        u = fa[top[u]];
    }
    if (dep[u] > dep[v]) swap(u, v);
    upd(1, 1, n, id[u], id[v], k);
}
int subtree_sum(int u) { return qry(1, 1, n, id[u], id[u] + sz[u] - 1); }`,
    note: "核心结论：重链在 dfs 序上连续，子树也连续。这两条性质撑起全部操作。" },

  { n: "可持久化线段树（主席树）", c: "数据结构", lv: 8, cx: "O(log n)",
    code: `int ls[N*40], rs[N*40], sum[N*40], rt[N], tot;
int update(int p, int l, int r, int x) {
    int q = ++tot; ls[q] = ls[p]; rs[q] = rs[p]; sum[q] = sum[p] + 1;
    if (l == r) return q;
    int m = (l + r) >> 1;
    if (x <= m) ls[q] = update(ls[p], l, m, x);
    else        rs[q] = update(rs[p], m+1, r, x);
    return q;
}
int kth(int p, int q, int l, int r, int k) {   // 区间 (p,q] 第 k 小
    if (l == r) return l;
    int m = (l + r) >> 1, c = sum[ls[q]] - sum[ls[p]];
    if (k <= c) return kth(ls[p], ls[q], l, m, k);
    return kth(rs[p], rs[q], m+1, r, k - c);
}`,
    note: "空间复杂度 O(n log n)，N*40 是保守估计。建树时先建空树 rt[0]。" },

  /* ---------------- 图论 ---------------- */
  { n: "链式前向星", c: "图论", lv: 6, cx: "O(n+m)",
    code: `int head[N], tot;
struct Edge { int to, nxt, w; } e[M];
void add(int u, int v, int w) {
    e[++tot] = {v, head[u], w}; head[u] = tot;
}
// 遍历
for (int i = head[u]; i; i = e[i].nxt) {
    int v = e[i].to, w = e[i].w;
}`,
    note: "边数组要开 2 倍（无向图双向加边）。head 初始化为 0，边从 1 开始编号。" },

  { n: "Dijkstra（堆优化）", c: "图论", lv: 6, cx: "O(m log n)",
    code: `struct Node { int u, d; bool operator<(const Node &o) const { return d > o.d; } };
void dijkstra(int s) {
    memset(dis, 0x3f, sizeof dis);
    dis[s] = 0;
    priority_queue<Node> q; q.push({s, 0});
    while (!q.empty()) {
        Node t = q.top(); q.pop();
        int u = t.u;
        if (t.d != dis[u]) continue;              // 懒惰删除
        for (int i = head[u]; i; i = e[i].nxt) {
            int v = e[i].to, w = e[i].w;
            if (dis[v] > dis[u] + w) {
                dis[v] = dis[u] + w;
                q.push({v, dis[v]});
            }
        }
    }
}`,
    note: "不能处理负权。0x3f3f3f3f 两倍不会溢出 int，这是它被广泛使用的原因。" },

  { n: "SPFA（判负环）", c: "图论", lv: 6, cx: "最坏 O(nm)",
    code: `bool spfa(int s) {          // 返回 true 表示有负环
    memset(dis, 0x3f, sizeof dis); dis[s] = 0;
    queue<int> q; q.push(s); inq[s] = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop(); inq[u] = 0;
        for (int i = head[u]; i; i = e[i].nxt) {
            int v = e[i].to, w = e[i].w;
            if (dis[v] > dis[u] + w) {
                dis[v] = dis[u] + w;
                cnt[v] = cnt[u] + 1;
                if (cnt[v] >= n) return true;
                if (!inq[v]) { q.push(v); inq[v] = 1; }
            }
        }
    }
    return false;
}`,
    note: "在网格图、菊花图上会被卡到 TLE。正权图一律用 Dijkstra，SPFA 只用于负权或判环。" },

  { n: "Kruskal（最小生成树）", c: "图论", lv: 6, cx: "O(m log m)",
    code: `sort(e + 1, e + m + 1, [](const Edge &a, const Edge &b) { return a.w < b.w; });
for (int i = 1; i <= n; i++) fa[i] = i;
int cnt = 0; long long ans = 0;
for (int i = 1; i <= m; i++) {
    int fx = find(e[i].u), fy = find(e[i].v);
    if (fx != fy) { fa[fx] = fy; ans += e[i].w; cnt++; }
    if (cnt == n - 1) break;
}
if (cnt < n - 1) puts("无法连通");`,
    note: "判无解必须检查 cnt == n-1。边按权排序后贪心，正确性来自切割性质。" },

  { n: "拓扑排序（Kahn）", c: "图论", lv: 6, cx: "O(n+m)",
    code: `queue<int> q;
for (int i = 1; i <= n; i++) if (!in[i]) q.push(i);
int cnt = 0;
while (!q.empty()) {
    int u = q.front(); q.pop(); top[++cnt] = u;
    for (int i = head[u]; i; i = e[i].nxt) {
        int v = e[i].to;
        if (--in[v] == 0) q.push(v);
    }
}
if (cnt < n) puts("存在环");`,
    note: "要字典序最小就把 queue 换成 priority_queue。判环看 cnt 是否等于 n。" },

  { n: "Tarjan 求强连通分量", c: "图论", lv: 7, cx: "O(n+m)",
    code: `void tarjan(int u) {
    dfn[u] = low[u] = ++idx;
    stk[++top] = u; ins[u] = 1;
    for (int i = head[u]; i; i = e[i].nxt) {
        int v = e[i].to;
        if (!dfn[v]) { tarjan(v); low[u] = min(low[u], low[v]); }
        else if (ins[v]) low[u] = min(low[u], dfn[v]);
    }
    if (low[u] == dfn[u]) {
        scc++;
        int v;
        do { v = stk[top--]; ins[v] = 0; bel[v] = scc; } while (v != u);
    }
}`,
    note: "low[u] 用 dfn[v] 而非 low[v] 更新（横向边不能走）。缩点后原图变成 DAG。" },

  { n: "割点与割边", c: "图论", lv: 7, cx: "O(n+m)",
    code: `void tarjan(int u, int fa) {
    dfn[u] = low[u] = ++idx; int child = 0;
    for (int i = head[u]; i; i = e[i].nxt) {
        int v = e[i].to;
        if (!dfn[v]) {
            tarjan(v, u); low[u] = min(low[u], low[v]); child++;
            if (low[v] >= dfn[u] && fa) cut[u] = 1;        // 割点
            if (low[v] >  dfn[u]) bridge[i] = bridge[i^1] = 1;  // 割边
        } else if (v != fa) low[u] = min(low[u], dfn[v]);
    }
    if (!fa && child > 1) cut[u] = 1;
}`,
    note: "割点条件 >=，割边条件 >，一字之差。根节点需单独判孩子数 > 1。" },

  { n: "倍增求 LCA", c: "图论", lv: 6, cx: "O(n log n) 预处理",
    code: `void dfs(int u, int f) {
    dep[u] = dep[f] + 1; up[u][0] = f;
    for (int k = 1; k <= LOG; k++) up[u][k] = up[up[u][k-1]][k-1];
    for (int v : g[u]) if (v != f) dfs(v, u);
}
int lca(int u, int v) {
    if (dep[u] < dep[v]) swap(u, v);
    int d = dep[u] - dep[v];
    for (int k = 0; k <= LOG; k++) if (d >> k & 1) u = up[u][k];
    if (u == v) return u;
    for (int k = LOG; k >= 0; k--)
        if (up[u][k] != up[v][k]) { u = up[u][k]; v = up[v][k]; }
    return up[u][0];
}`,
    note: "LOG 取 log2(n)+1。第二次必须倒序枚举，正序会跳过头。" },

  { n: "匈牙利算法（二分图最大匹配）", c: "图论", lv: 8, cx: "O(nm)",
    code: `bool vis[N]; int match[N];
bool dfs(int u) {
    for (int v : g[u]) {
        if (vis[v]) continue;
        vis[v] = 1;
        if (!match[v] || dfs(match[v])) { match[v] = u; return true; }
    }
    return false;
}
int maxmatch() {
    int res = 0;
    for (int i = 1; i <= n; i++) {
        memset(vis, 0, sizeof vis);
        if (dfs(i)) res++;
    }
    return res;
}`,
    note: "vis 每轮必须清空，否则同一轮会重复访问。复杂度 O(nm)，稠密图考虑 Dinic。" },

  { n: "Dinic（最大流）", c: "图论", lv: 8, cx: "O(n²m)",
    code: `bool bfs() {
    memset(dep, 0, sizeof dep);
    queue<int> q; q.push(S); dep[S] = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int i = head[u]; i; i = e[i].nxt) {
            int v = e[i].to;
            if (e[i].w && !dep[v]) { dep[v] = dep[u] + 1; q.push(v); }
        }
    }
    return dep[T];
}
int dfs(int u, int f) {
    if (u == T) return f;
    for (int &i = cur[u]; i; i = e[i].nxt) {
        int v = e[i].to;
        if (e[i].w && dep[v] == dep[u] + 1) {
            int t = dfs(v, min(f, e[i].w));
            if (t) { e[i].w -= t; e[i^1].w += t; return t; }
        }
    }
    return 0;
}
long long dinic() {
    long long flow = 0;
    while (bfs()) {
        memcpy(cur, head, sizeof head);
        while (int f = dfs(S, INF)) flow += f;
    }
    return flow;
}`,
    note: "加边必须成对：正向 w，反向 0，且用 i^1 取反向边。当前弧优化 cur 不可省。" },

  { n: "2-SAT", c: "图论", lv: 8, cx: "O(n+m)",
    code: `// 变量 i 取真: 2*i, 取假: 2*i+1（或按习惯相反，全篇统一即可）
// 条件 (a == x) 或 (b == y)：
//   add(a ^ !x, b ^ y); add(b ^ !y, a ^ x);
// 跑 Tarjan 求 SCC 后：
for (int i = 1; i <= n; i++) {
    if (bel[2*i] == bel[2*i+1]) { puts("IMPOSSIBLE"); return 0; }
    ans[i] = (bel[2*i] < bel[2*i+1]);   // 取 SCC 编号较小者
}`,
    note: "建图是难点：把「或」转成「蕴含」。SCC 编号顺序决定取值方向，Tarjan 下取较小者。" },

  /* ---------------- 动态规划 ---------------- */
  { n: "01 背包（一维）", c: "DP", lv: 5, cx: "O(nV)",
    code: `for (int i = 1; i <= n; i++)
    for (int j = V; j >= w[i]; j--)
        f[j] = max(f[j], f[j - w[i]] + v[i]);`,
    note: "内层必须倒序，否则同一物品会被重复选取，退化成完全背包。" },

  { n: "完全背包", c: "DP", lv: 5, cx: "O(nV)",
    code: `for (int i = 1; i <= n; i++)
    for (int j = w[i]; j <= V; j++)
        f[j] = max(f[j], f[j - w[i]] + v[i]);`,
    note: "与 01 背包只差一个循环方向。正序意味着允许同一物品多次使用。" },

  { n: "多重背包（二进制拆分）", c: "DP", lv: 6, cx: "O(V Σlog c)",
    code: `for (int i = 1; i <= n; i++) {
    int c = cnt[i], k = 1;
    while (c) {
        int t = min(k, c);
        for (int j = V; j >= t * w[i]; j--)
            f[j] = max(f[j], f[j - t*w[i]] + t*v[i]);
        c -= t; k <<= 1;
    }
}`,
    note: "把 c 拆成 1,2,4,... 的组合后转 01 背包。单调队列优化可做到 O(nV)。" },

  { n: "LIS（O(n log n)）", c: "DP", lv: 5, cx: "O(n log n)",
    code: `vector<int> d;
for (int i = 1; i <= n; i++) {
    auto it = lower_bound(d.begin(), d.end(), a[i]);   // 严格上升用 lower_bound
    if (it == d.end()) d.push_back(a[i]);
    else *it = a[i];
}
int lis = d.size();`,
    note: "d 数组不是真正的 LIS 序列，只是长度信息。非降用 upper_bound。" },

  { n: "LCS", c: "DP", lv: 5, cx: "O(nm)",
    code: `for (int i = 1; i <= n; i++)
    for (int j = 1; j <= m; j++)
        if (a[i] == b[j]) f[i][j] = f[i-1][j-1] + 1;
        else f[i][j] = max(f[i-1][j], f[i][j-1]);`,
    note: "LCS 可转成 LIS 做到 O(n log n)（要求元素互不相同）。" },

  { n: "区间 DP", c: "DP", lv: 5, cx: "O(n³)",
    code: `for (int len = 2; len <= n; len++)
    for (int l = 1; l + len - 1 <= n; l++) {
        int r = l + len - 1;
        f[l][r] = INF;
        for (int k = l; k < r; k++)
            f[l][r] = min(f[l][r], f[l][k] + f[k+1][r] + cost(l, r));
    }`,
    note: "枚举顺序必须是「长度优先」，因为大区间依赖小区间。环形问题破环成链、数组开 2 倍。" },

  { n: "状压 DP（TSP）", c: "DP", lv: 7, cx: "O(2ⁿ n²)",
    code: `memset(dp, 0x3f, sizeof dp);
dp[1][0] = 0;
for (int S = 1; S < (1 << n); S++)
    for (int i = 0; i < n; i++) if (S >> i & 1)
        for (int j = 0; j < n; j++) if (!(S >> j & 1))
            dp[S | 1 << j][j] = min(dp[S | 1 << j][j], dp[S][i] + w[i][j]);
int ans = INF;
for (int i = 1; i < n; i++) ans = min(ans, dp[(1<<n)-1][i] + w[i][0]);`,
    note: "n ≤ 20 才可用。转移前判状态合法性（如相邻不能同时选）能大幅剪枝。" },

  { n: "树形 DP（子树合并）", c: "DP", lv: 6, cx: "O(n²) 或 O(n)",
    code: `void dfs(int u, int fa) {
    sz[u] = 1; f[u][0] = 0; f[u][1] = val[u];
    for (int v : g[u]) if (v != fa) {
        dfs(v, u);
        for (int j = min(sz[u], K); j >= 0; j--)
            for (int k = 0; k <= min(sz[v], K - j); k++)
                f[u][j+k] = max(f[u][j+k], f[u][j] + f[v][k]);
        sz[u] += sz[v];
    }
}`,
    note: "树上背包的复杂度是 O(n²) 而不是 O(nK²)，因为按子树大小限制上界。" },

  { n: "数位 DP", c: "DP", lv: 7, cx: "O(位数 × 状态)",
    code: `long long dfs(int pos, int pre, bool lim, bool lead) {
    if (!pos) return 1;
    if (!lim && !lead && f[pos][pre] != -1) return f[pos][pre];
    int up = lim ? d[pos] : 9;
    long long s = 0;
    for (int i = 0; i <= up; i++)
        s += dfs(pos - 1, i, lim && i == up, lead && !i);
    if (!lim && !lead) f[pos][pre] = s;
    return s;
}
long long solve(long long x) {
    int len = 0;
    while (x) { d[++len] = x % 10; x /= 10; }
    memset(f, -1, sizeof f);
    return dfs(len, 10, true, true);
}`,
    note: "记忆化只在 !lim && !lead 时生效。答案用 solve(r) - solve(l-1)。" },

  { n: "单调队列优化 DP", c: "DP", lv: 8, cx: "O(n)",
    code: `// f[i] = min_{j in [i-k, i-1]} f[j] + a[i]
for (int i = 1; i <= n; i++) {
    while (h <= t && q[h] < i - k) h++;
    f[i] = f[q[h]] + a[i];
    while (h <= t && f[q[t]] >= f[i]) t--;
    q[++t] = i;
}`,
    note: "识别特征：转移区间是滑动窗口。必须先更新 f[i] 再入队，顺序反了会用到自己。" },

  /* ---------------- 字符串 ---------------- */
  { n: "KMP（next 数组）", c: "字符串", lv: 6, cx: "O(n+m)",
    code: `void getnext(const char *p, int m, int *ne) {
    ne[0] = 0;
    for (int i = 1, j = 0; i < m; i++) {
        while (j && p[i] != p[j]) j = ne[j-1];
        if (p[i] == p[j]) j++;
        ne[i] = j;
    }
}
void kmp(const char *s, int n, const char *p, int m, int *ne) {
    for (int i = 0, j = 0; i < n; i++) {
        while (j && s[i] != p[j]) j = ne[j-1];
        if (s[i] == p[j]) j++;
        if (j == m) { printf("%d\\n", i - m + 2); j = ne[j-1]; }
    }
}`,
    note: "ne[i] 表示 p[0..i] 的最长公共前后缀长度（下标从 0 起）。失配时跳 ne[j-1] 而非 ne[j]。" },

  { n: "字符串哈希（双哈希）", c: "字符串", lv: 6, cx: "O(n) 预处理",
    code: `const int P1 = 131, M1 = 1e9+7, P2 = 13331, M2 = 998244353;
void init() {
    pw1[0] = pw2[0] = 1;
    for (int i = 1; i <= n; i++) {
        pw1[i] = 1LL * pw1[i-1] * P1 % M1;
        pw2[i] = 1LL * pw2[i-1] * P2 % M2;
        h1[i] = (1LL * h1[i-1] * P1 + s[i]) % M1;
        h2[i] = (1LL * h2[i-1] * P2 + s[i]) % M2;
    }
}
pair<int,int> get(int l, int r) {
    int a = (h1[r] - 1LL * h1[l-1] * pw1[r-l+1] % M1 + M1) % M1;
    int b = (h2[r] - 1LL * h2[l-1] * pw2[r-l+1] % M2 + M2) % M2;
    return {a, b};
}`,
    note: "单哈希可被构造卡掉，正式比赛用双哈希。减法后必须 +M 再取模。" },

  { n: "Manacher（最长回文子串）", c: "字符串", lv: 7, cx: "O(n)",
    code: `int manacher(char *s, int n) {
    static char t[N]; static int p[N];
    int m = 0; t[m++] = '^';
    for (int i = 0; i < n; i++) { t[m++] = '#'; t[m++] = s[i]; }
    t[m++] = '#'; t[m++] = '$';
    int c = 0, r = 0, ans = 0;
    for (int i = 1; i < m - 1; i++) {
        p[i] = (i < r) ? min(r - i, p[2*c - i]) : 0;
        while (t[i + p[i] + 1] == t[i - p[i] - 1]) p[i]++;
        if (i + p[i] > r) { c = i; r = i + p[i]; }
        ans = max(ans, p[i]);
    }
    return ans;   // 原串中的回文长度
}`,
    note: "插入分隔符后奇偶回文统一处理。p[i] 即以 i 为中心的回文半径。" },

  { n: "Z 函数（扩展 KMP）", c: "字符串", lv: 8, cx: "O(n)",
    code: `void zfunc(const char *s, int n, int *z) {
    z[0] = n;
    for (int i = 1, l = 0, r = 0; i < n; i++) {
        if (i < r) z[i] = min(r - i, z[i - l]);
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
}`,
    note: "z[i] 是 s 与 s[i..] 的最长公共前缀。求匹配时把模式串拼在原串前，用分隔符隔开。" },

  { n: "AC 自动机", c: "字符串", lv: 8, cx: "O(ΣL + n)",
    code: `int ch[N][26], fail[N], cnt[N], tot;
void insert(char *s) {
    int p = 0;
    for (int i = 0; s[i]; i++) {
        int c = s[i] - 'a';
        if (!ch[p][c]) ch[p][c] = ++tot;
        p = ch[p][c];
    }
    cnt[p]++;
}
void build() {
    queue<int> q;
    for (int c = 0; c < 26; c++) if (ch[0][c]) q.push(ch[0][c]);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int c = 0; c < 26; c++) {
            int v = ch[u][c];
            if (v) { fail[v] = ch[fail[u]][c]; q.push(v); }
            else ch[u][c] = ch[fail[u]][c];      // 失配指针下推，形成 Trie 图
        }
    }
}`,
    note: "build 里的 else 分支是「Trie 图」优化，省去查询时的 while 跳 fail。" },

  /* ---------------- 数学 ---------------- */
  { n: "快速幂", c: "数学", lv: 3, cx: "O(log b)",
    code: `long long qpow(long long a, long long b, long long mod) {
    long long r = 1 % mod;
    while (b) {
        if (b & 1) r = r * a % mod;
        a = a * a % mod;
        b >>= 1;
    }
    return r;
}`,
    note: "初始化为 1 % mod 而不是 1，否则 mod=1 时返回错误值。" },

  { n: "扩展欧几里得", c: "数学", lv: 7, cx: "O(log n)",
    code: `long long exgcd(long long a, long long b, long long &x, long long &y) {
    if (!b) { x = 1; y = 0; return a; }
    long long d = exgcd(b, a % b, y, x);
    y -= a / b * x;
    return d;
}`,
    note: "返回 gcd(a,b)，同时求出 ax+by=gcd 的一组解。通解 x + k·(b/d)。" },

  { n: "线性筛（素数 + 欧拉函数）", c: "数学", lv: 7, cx: "O(n)",
    code: `void sieve(int n) {
    phi[1] = 1;
    for (int i = 2; i <= n; i++) {
        if (!vis[i]) { pr[++cnt] = i; phi[i] = i - 1; }
        for (int j = 1; j <= cnt && 1LL * i * pr[j] <= n; j++) {
            vis[i * pr[j]] = 1;
            if (i % pr[j] == 0) {
                phi[i * pr[j]] = phi[i] * pr[j];
                break;                      // 保证每个数只被最小质因子筛一次
            }
            phi[i * pr[j]] = phi[i] * (pr[j] - 1);
        }
    }
}`,
    note: "break 是线性复杂度的关键。i * pr[j] 要用 1LL 防止溢出。" },

  { n: "乘法逆元（费马 + 线性递推）", c: "数学", lv: 7, cx: "O(n)",
    code: `// mod 为质数时
long long inv(long long a) { return qpow(a, mod - 2, mod); }

// 线性递推求 1..n 的逆元
inv[1] = 1;
for (int i = 2; i <= n; i++)
    inv[i] = (mod - mod / i) * inv[mod % i] % mod;`,
    note: "要求 gcd(a, mod) = 1。非质数模用 exgcd。组合数用阶乘逆元时注意从大到小递推。" },

  { n: "组合数（阶乘逆元）", c: "数学", lv: 6, cx: "O(n) 预处理",
    code: `fac[0] = 1;
for (int i = 1; i <= n; i++) fac[i] = fac[i-1] * i % mod;
ifac[n] = qpow(fac[n], mod - 2, mod);
for (int i = n; i >= 1; i--) ifac[i-1] = ifac[i] * i % mod;
auto C = [&](int n, int m) -> long long {
    if (m < 0 || m > n) return 0;
    return fac[n] * ifac[m] % mod * ifac[n-m] % mod;
};`,
    note: "mod 必须是大于 n 的质数。否则需用 Lucas 定理或 CRT 合并。" },

  { n: "中国剩余定理（CRT）", c: "数学", lv: 7, cx: "O(n log M)",
    code: `// x ≡ a[i] (mod m[i])，m 两两互质
long long CRT(int n, long long *a, long long *m) {
    long long M = 1, ans = 0;
    for (int i = 1; i <= n; i++) M *= m[i];
    for (int i = 1; i <= n; i++) {
        long long Mi = M / m[i], x, y;
        exgcd(Mi, m[i], x, y);
        ans = (ans + a[i] * Mi % M * ((x % M + M) % M)) % M;
    }
    return (ans % M + M) % M;
}`,
    note: "模数不互质时需用「扩展 CRT」，逐个合并方程。" },

  { n: "高斯消元（实数解）", c: "数学", lv: 7, cx: "O(n³)",
    code: `for (int i = 1; i <= n; i++) {
    int p = i;
    for (int j = i + 1; j <= n; j++)
        if (fabs(a[j][i]) > fabs(a[p][i])) p = j;
    if (fabs(a[p][i]) < eps) { puts("No Solution"); return 0; }
    swap(a[i], a[p]);
    for (int j = 1; j <= n; j++) {
        if (i == j) continue;
        double t = a[j][i] / a[i][i];
        for (int k = i; k <= n + 1; k++) a[j][k] -= t * a[i][k];
    }
}
for (int i = 1; i <= n; i++) printf("%.2f\\n", a[i][n+1] / a[i][i]);`,
    note: "必须选主元（列主元消去），否则精度会崩。eps 取 1e-8 左右。" },

  { n: "矩阵快速幂", c: "数学", lv: 6, cx: "O(n³ log k)",
    code: `struct Mat {
    int n; long long a[105][105];
    Mat(int n = 0) : n(n) { memset(a, 0, sizeof a); }
};
Mat operator*(const Mat &A, const Mat &B) {
    Mat C(A.n);
    for (int i = 0; i < A.n; i++)
        for (int k = 0; k < A.n; k++) {
            if (!A.a[i][k]) continue;
            for (int j = 0; j < A.n; j++)
                C.a[i][j] = (C.a[i][j] + A.a[i][k] * B.a[k][j]) % mod;
        }
    return C;
}
Mat qpow(Mat A, long long b) {
    Mat R(A.n);
    for (int i = 0; i < A.n; i++) R.a[i][i] = 1;
    while (b) { if (b & 1) R = R * A; A = A * A; b >>= 1; }
    return R;
}`,
    note: "关键在于构造转移矩阵。斐波那契用 [[1,1],[1,0]]，注意矩阵乘法不满足交换律。" },

  { n: "容斥原理", c: "数学", lv: 7, cx: "O(2ⁿ)",
    code: `long long ans = 0;
for (int S = 1; S < (1 << n); S++) {
    long long lcm = 1; int bits = 0;
    for (int i = 0; i < n; i++) if (S >> i & 1) {
        lcm = lcm / gcd(lcm, a[i]) * a[i];
        bits++;
    }
    ans += (bits & 1 ? 1 : -1) * (m / lcm);
}`,
    note: "「至少一个满足」的标准形式。lcm 可能溢出，需提前判断是否超过上界。" }
];
