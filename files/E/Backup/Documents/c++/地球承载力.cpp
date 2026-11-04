#include<iostream>
#include<iomanip>
using namespace std;

int main()
{
    double x, a, y, b;
    cin >> x >> a >> y >> b;
    
    // 计算每年新生资源（最多养活人数）
    double z = (y * b - x * a) / (b - a);
    
    // 保留两位小数输出
    cout << fixed << setprecision(2) << z << endl;
    
    return 0;
}
