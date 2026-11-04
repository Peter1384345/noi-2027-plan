#include <bits/stdc++.h>
using namespace std;

typedef long long ll;
const int N = 505;
const ll MOD = 998244353;

int n, m;
char s[N];
int a[N];
ll f[N][N][N];
ll fac[N], inv[N];

ll ksm(ll a, ll b) {
    ll r = 1;
    while (b) {
        if (b & 1) r = r * a % MOD;
        a = a * a % MOD;
        b >>= 1;
    }
    return r;
}

void init() {
    fac[0] = 1;
    for (int i = 1; i <= n; i++) fac[i] = fac[i - 1] * i % MOD;
    inv[n] = ksm(fac[n], MOD - 2);
    for (int i = n - 1; i >= 0; i--) inv[i] = inv[i + 1] * (i + 1) % MOD;
}

int main() {
    scanf("%d%d", &n, &m);
    scanf("%s", s + 1);
    for (int i = 1; i <= n; i++) {
        int c; scanf("%d", &c);
        a[c]++;
    }
    for (int i = 1; i <= n; i++) a[i] += a[i - 1];
    init();

    f[0][0][0] = 1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j <= i; j++) {
            for (int k = 0; k <= i; k++) {
                ll cur = f[i][j][k];
                if (!cur) continue;
                if (s[i + 1] == '0') {
                    f[i + 1][j + 1][k] = (f[i + 1][j + 1][k] + cur) % MOD;
                } else {
                    f[i + 1][j][k] = (f[i + 1][j][k] + cur) % MOD;
                    ll x = (a[j] - k) % MOD;
                    if (x < 0) x += MOD;
                    f[i + 1][j][k + 1] = (f[i + 1][j][k + 1] - x * cur % MOD + MOD) % MOD;
                    f[i + 1][j + 1][k + 1] = (f[i + 1][j + 1][k + 1] + x * cur) % MOD;
                }
            }
        }
    }

    ll ans = 0;
    for (int j = 0; j <= n - m; j++) {
        for (int k = 0; k <= n; k++) {
            ans = (ans + f[n][j][k] * fac[n - k]) % MOD;
        }
    }
    printf("%lld\n", ans);
    return 0;
}
