#include<iostream>
#include<iomanip>
using namespace std;
int main()
{
    double r;
    const double pi = 3.14159;
    cin >> r;
    cout << fixed << setprecision(4) << 2 * r << " "  << 2 * pi * r << " " << pi * r * r << endl;
    return 0;
}
