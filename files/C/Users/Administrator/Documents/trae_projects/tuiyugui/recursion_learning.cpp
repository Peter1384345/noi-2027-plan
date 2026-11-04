#include <iostream>
#include <string>
#include <windows.h>

using namespace std;

void show_problem_factorial() {
    cout << endl << "========================================" << endl;
    cout << "            题目描述" << endl;
    cout << "========================================" << endl;
    cout << "【题目名称】阶乘计算" << endl;
    cout << "【题目来源】洛谷 B2003" << endl;
    cout << "【题目难度】入门" << endl;
    cout << endl;
    cout << "题目描述：" << endl;
    cout << "  输入一个正整数 n，输出 n 的阶乘。" << endl;
    cout << "  阶乘定义：n! = n × (n-1) × (n-2) × ... × 1" << endl;
    cout << "  规定：0! = 1, 1! = 1" << endl;
    cout << endl;
    cout << "输入格式：" << endl;
    cout << "  一个正整数 n (1 ≤ n ≤ 20)" << endl;
    cout << endl;
    cout << "输出格式：" << endl;
    cout << "  一个整数，表示 n 的阶乘" << endl;
    cout << endl;
    cout << "输入输出示例：" << endl;
    cout << "  输入：5" << endl;
    cout << "  输出：120" << endl;
    cout << "========================================" << endl;
}

long long factorial_recursive(int n) {
    if (n == 0 || n == 1) return 1;
    return n * factorial_recursive(n - 1);
}

long long factorial_iterative(int n) {
    long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

void solve_factorial() {
    show_problem_factorial();
    
    int n;
    cout << endl << "请输入 n：";
    cin >> n;
    
    cout << endl << "方法一：递归求解" << endl;
    cout << "----------------------------------------" << endl;
    cout << "递归调用过程：" << endl;
    cout << "factorial(" << n << ")";
    for (int i = n; i > 1; --i) {
        cout << " → " << i << " × factorial(" << i - 1 << ")";
    }
    cout << " → 1 × 1" << endl;
    cout << "结果：" << factorial_recursive(n) << endl;
    
    cout << endl << "方法二：递推求解" << endl;
    cout << "----------------------------------------" << endl;
    cout << "递推过程：" << endl;
    long long result = 1;
    cout << "f(0) = 1" << endl;
    for (int i = 1; i <= n; ++i) {
        result *= i;
        cout << "f(" << i << ") = f(" << i - 1 << ") × " << i << " = " << result << endl;
    }
    cout << "结果：" << result << endl;
}

void show_problem_fibonacci() {
    cout << endl << "========================================" << endl;
    cout << "            题目描述" << endl;
    cout << "========================================" << endl;
    cout << "【题目名称】斐波那契数列" << endl;
    cout << "【题目来源】洛谷 B2064" << endl;
    cout << "【题目难度】入门" << endl;
    cout << endl;
    cout << "题目描述：" << endl;
    cout << "  斐波那契数列的定义如下：" << endl;
    cout << "  F(0) = 0, F(1) = 1" << endl;
    cout << "  F(n) = F(n-1) + F(n-2) (n ≥ 2)" << endl;
    cout << "  输入 n，求 F(n) 的值。" << endl;
    cout << endl;
    cout << "输入格式：" << endl;
    cout << "  一个整数 n (0 ≤ n ≤ 50)" << endl;
    cout << endl;
    cout << "输出格式：" << endl;
    cout << "  一个整数，表示 F(n) 的值" << endl;
    cout << endl;
    cout << "输入输出示例：" << endl;
    cout << "  输入：10" << endl;
    cout << "  输出：55" << endl;
    cout << "========================================" << endl;
}

long long fibonacci_memoized(int n, long long memo[]) {
    if (n <= 1) return n;
    if (memo[n] != 0) return memo[n];
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo);
    return memo[n];
}

long long fibonacci_iterative(int n) {
    if (n <= 1) return n;
    long long a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
        long long c = a + b;
        a = b;
        b = c;
    }
    return b;
}

void solve_fibonacci() {
    show_problem_fibonacci();
    
    int n;
    cout << endl << "请输入 n：";
    cin >> n;
    
    cout << endl << "方法一：递归求解（记忆化优化）" << endl;
    cout << "----------------------------------------" << endl;
    long long memo[100] = {0};
    long long r_result = fibonacci_memoized(n, memo);
    cout << "递归树分析：" << endl;
    cout << "  标准递归时间复杂度：O(2^n)（存在大量重复计算）" << endl;
    cout << "  记忆化优化时间复杂度：O(n)" << endl;
    cout << "结果：" << r_result << endl;
    
    cout << endl << "方法二：递推求解" << endl;
    cout << "----------------------------------------" << endl;
    cout << "递推过程：" << endl;
    if (n <= 1) {
        cout << "F(" << n << ") = " << n << endl;
    } else {
        long long a = 0, b = 1;
        cout << "F(0) = " << a << endl;
        cout << "F(1) = " << b << endl;
        for (int i = 2; i <= n; ++i) {
            long long c = a + b;
            cout << "F(" << i << ") = F(" << i - 2 << ") + F(" << i - 1 << ") = " << a << " + " << b << " = " << c << endl;
            a = b;
            b = c;
        }
    }
    cout << "结果：" << fibonacci_iterative(n) << endl;
}

void show_problem_stairs() {
    cout << endl << "========================================" << endl;
    cout << "            题目描述" << endl;
    cout << "========================================" << endl;
    cout << "【题目名称】数楼梯" << endl;
    cout << "【题目来源】洛谷 P1255" << endl;
    cout << "【题目难度】普及-" << endl;
    cout << endl;
    cout << "题目描述：" << endl;
    cout << "  楼梯有 n 阶台阶，上楼可以一步上 1 阶，也可以一步上 2 阶。" << endl;
    cout << "  编一个程序，计算共有多少种不同的走法。" << endl;
    cout << endl;
    cout << "输入格式：" << endl;
    cout << "  一个正整数 n (1 ≤ n ≤ 50)" << endl;
    cout << endl;
    cout << "输出格式：" << endl;
    cout << "  一个整数，表示走法数" << endl;
    cout << endl;
    cout << "输入输出示例：" << endl;
    cout << "  输入：5" << endl;
    cout << "  输出：8" << endl;
    cout << endl;
    cout << "样例说明：" << endl;
    cout << "  5 阶楼梯的 8 种走法：" << endl;
    cout << "  1+1+1+1+1" << endl;
    cout << "  1+1+1+2" << endl;
    cout << "  1+1+2+1" << endl;
    cout << "  1+2+1+1" << endl;
    cout << "  2+1+1+1" << endl;
    cout << "  1+2+2" << endl;
    cout << "  2+1+2" << endl;
    cout << "  2+2+1" << endl;
    cout << "========================================" << endl;
}

long long climb_stairs_memoized(int n, long long memo[]) {
    if (n == 1) return 1;
    if (n == 2) return 2;
    if (memo[n] != 0) return memo[n];
    memo[n] = climb_stairs_memoized(n - 1, memo) + climb_stairs_memoized(n - 2, memo);
    return memo[n];
}

long long climb_stairs_iterative(int n) {
    if (n == 1) return 1;
    if (n == 2) return 2;
    long long a = 1, b = 2;
    for (int i = 3; i <= n; ++i) {
        long long c = a + b;
        a = b;
        b = c;
    }
    return b;
}

void solve_stairs() {
    show_problem_stairs();
    
    int n;
    cout << endl << "请输入 n：";
    cin >> n;
    
    cout << endl << "方法一：递归求解（记忆化优化）" << endl;
    cout << "----------------------------------------" << endl;
    cout << "递归思想：" << endl;
    cout << "  f(n) = f(n-1) + f(n-2)" << endl;
    cout << "  解释：到第 n 阶可以从第 n-1 阶走 1 步，或从第 n-2 阶走 2 步" << endl;
    long long memo[100] = {0};
    cout << "结果：" << climb_stairs_memoized(n, memo) << endl;
    
    cout << endl << "方法二：递推求解" << endl;
    cout << "----------------------------------------" << endl;
    cout << "递推过程：" << endl;
    if (n == 1) {
        cout << "f(1) = 1" << endl;
    } else if (n == 2) {
        cout << "f(1) = 1" << endl;
        cout << "f(2) = 2" << endl;
    } else {
        long long a = 1, b = 2;
        cout << "f(1) = 1" << endl;
        cout << "f(2) = 2" << endl;
        for (int i = 3; i <= n; ++i) {
            long long c = a + b;
            cout << "f(" << i << ") = f(" << i - 2 << ") + f(" << i - 1 << ") = " << a << " + " << b << " = " << c << endl;
            a = b;
            b = c;
        }
    }
    cout << "结果：" << climb_stairs_iterative(n) << endl;
}

void show_problem_hanoi() {
    cout << endl << "========================================" << endl;
    cout << "            题目描述" << endl;
    cout << "========================================" << endl;
    cout << "【题目名称】汉诺塔问题" << endl;
    cout << "【题目来源】洛谷经典递归题" << endl;
    cout << "【题目难度】普及" << endl;
    cout << endl;
    cout << "题目描述：" << endl;
    cout << "  有三根柱子 A、B、C。A 柱上有 n 个大小不同的圆盘，" << endl;
    cout << "  从上到下依次增大。要求将所有圆盘从 A 柱移到 C 柱，" << endl;
    cout << "  每次只能移动一个圆盘，且大盘不能放在小盘上面。" << endl;
    cout << endl;
    cout << "输入格式：" << endl;
    cout << "  一个正整数 n (1 ≤ n ≤ 10)" << endl;
    cout << endl;
    cout << "输出格式：" << endl;
    cout << "  输出每一步的移动操作" << endl;
    cout << endl;
    cout << "输入输出示例：" << endl;
    cout << "  输入：3" << endl;
    cout << "  输出：" << endl;
    cout << "  A -> C" << endl;
    cout << "  A -> B" << endl;
    cout << "  C -> B" << endl;
    cout << "  A -> C" << endl;
    cout << "  B -> A" << endl;
    cout << "  B -> C" << endl;
    cout << "  A -> C" << endl;
    cout << endl;
    cout << "提示：" << endl;
    cout << "  n 个圆盘需要移动 2^n - 1 次" << endl;
    cout << "========================================" << endl;
}

void tower_of_hanoi(int n, char source, char target, char auxiliary) {
    if (n == 1) {
        cout << "  " << source << " -> " << target << endl;
        return;
    }
    tower_of_hanoi(n - 1, source, auxiliary, target);
    cout << "  " << source << " -> " << target << endl;
    tower_of_hanoi(n - 1, auxiliary, target, source);
}

void solve_hanoi() {
    show_problem_hanoi();
    
    int n;
    cout << endl << "请输入 n：";
    cin >> n;
    
    cout << endl << "方法：递归求解" << endl;
    cout << "----------------------------------------" << endl;
    cout << "递归思想：" << endl;
    cout << "  1. 将 n-1 个圆盘从 A 移到 B（借助 C）" << endl;
    cout << "  2. 将第 n 个圆盘从 A 移到 C" << endl;
    cout << "  3. 将 n-1 个圆盘从 B 移到 C（借助 A）" << endl;
    cout << endl << "移动步骤：" << endl;
    tower_of_hanoi(n, 'A', 'C', 'B');
    cout << endl << "总移动次数：" << ((1LL << n) - 1) << " 次" << endl;
}

void show_summary() {
    cout << endl << "========================================" << endl;
    cout << "          递归与递推总结" << endl;
    cout << "========================================" << endl;
    cout << endl;
    cout << "【递归 (Recursion)】" << endl;
    cout << "  定义：函数调用自身的编程技巧" << endl;
    cout << "  三要素：" << endl;
    cout << "    1. 递归边界：问题的最小解（基准情况）" << endl;
    cout << "    2. 递归式：将问题分解为更小的子问题" << endl;
    cout << "    3. 递归返回：将子问题的解合并为原问题的解" << endl;
    cout << endl;
    cout << "【递推 (Iteration)】" << endl;
    cout << "  定义：从已知条件出发，逐步计算出后续结果" << endl;
    cout << "  特点：" << endl;
    cout << "    1. 从初始状态开始" << endl;
    cout << "    2. 通过循环逐步计算" << endl;
    cout << "    3. 通常空间和时间效率更高" << endl;
    cout << endl;
    cout << "【对比】" << endl;
    cout << "  递归：代码简洁，逻辑清晰，但可能栈溢出" << endl;
    cout << "  递推：代码繁琐，但效率更高，无栈溢出风险" << endl;
    cout << endl;
    cout << "【常见应用】" << endl;
    cout << "  递归：树遍历、分治算法、回溯算法" << endl;
    cout << "  递推：动态规划、斐波那契数列、组合计数" << endl;
    cout << endl;
    cout << "【优化技巧】" << endl;
    cout << "  1. 记忆化搜索：用数组存储已计算的结果" << endl;
    cout << "  2. 递推优化：用滚动数组减少空间复杂度" << endl;
    cout << "========================================" << endl;
}

void show_menu() {
    cout << endl << "========================================" << endl;
    cout << "    递归与递推学习程序（洛谷风格）" << endl;
    cout << "========================================" << endl;
    cout << endl;
    cout << "【入门】" << endl;
    cout << "  1. 阶乘计算       [B2003]" << endl;
    cout << "  2. 斐波那契数列   [B2064]" << endl;
    cout << endl;
    cout << "【普及】" << endl;
    cout << "  3. 数楼梯         [P1255]" << endl;
    cout << "  4. 汉诺塔问题     [经典]" << endl;
    cout << endl;
    cout << "【其他】" << endl;
    cout << "  5. 知识总结" << endl;
    cout << "  0. 退出" << endl;
    cout << endl;
    cout << "========================================" << endl;
}

int main() {
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);
    
    cout << "欢迎使用递归与递推学习程序！" << endl;
    cout << "本程序按照洛谷题单风格设计，包含经典算法题目。" << endl;
    
    while (true) {
        show_menu();
        cout << "请选择题目 (0-5): ";
        int choice;
        cin >> choice;
        
        if (choice == 0) {
            cout << endl << "感谢使用，再见！" << endl;
            break;
        }
        
        else if (choice == 1) {
            solve_factorial();
        }
        
        else if (choice == 2) {
            solve_fibonacci();
        }
        
        else if (choice == 3) {
            solve_stairs();
        }
        
        else if (choice == 4) {
            solve_hanoi();
        }
        
        else if (choice == 5) {
            show_summary();
        }
        
        else {
            cout << endl << "无效选择，请输入 0-5 之间的数字！" << endl;
        }
        
        cout << endl << "----------------------------------------" << endl;
        cout << "按回车键继续...";
        cin.ignore();
        cin.get();
    }
    
    return 0;
}