#include<iostream>
using namespace std;
int main()
{
    double N;
    cin >> N;
    if(N > 0) {
        cout << "positive";
    }  
    else if(N < 0) {
        cout << "negative";
    }
    else {
        cout << "zero";
    }
    return 0;
}
