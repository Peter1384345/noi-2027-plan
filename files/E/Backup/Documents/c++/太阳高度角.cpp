#include<iostream>
#include<cmath>
using namespace std;
int main()
{
	float a,x;//定义影长浮点数a,弧度x
	cout<<"请输入影长:";
	cin>>a;
	x=atan(1.0/a)*180/3.14159265358 ;
	cout<<"太阳照射角为"<<x<<"度"<<endl;
	while(true){
		cout<<"请输入影长:";
		cin>>a;
		x=atan(1.0/a)*180/3.1415926535 ;
		cout<<"太阳照射角为"<<x<<"度"<<endl;
		if(a == 10086){
			break;
		}
	}
	return 0;
}
