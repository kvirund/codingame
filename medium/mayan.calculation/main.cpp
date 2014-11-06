/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <map>
#include <list>

#include <assert.h>

using namespace std;

std::map<std::string, unsigned long long int> numbers;

void print_number(std::string number, unsigned long long int H)
{
    unsigned long long int nl = number.length();
    assert(0 == nl % H);
    unsigned long long int W = nl/H;
    for (unsigned long long int i = 0; i < H; i++)
    {
        std::cout << number.substr(i*W, W) << std::endl;
    }
}

int main()
{
    unsigned long long int L;
    unsigned long long int H;
    cin >> L >> H;
    cin.ignore();
    
    std::vector<std::string> nums(20);
    for (unsigned long long int i = 0; i < H; i++)
    {
        string numeral;
        cin >> numeral;
        cin.ignore();
        
        const size_t nl = numeral.length();
        assert(L*20 == nl);
        for (size_t i = 0; i < 20; i++)
        {
            nums[i] += numeral.substr(L*i, L);
        }
    }
    
    for (unsigned long long int i = 0; i < 20; i++)
    {
        cerr.width(2);
        cerr << i << ": " << nums[i] << endl;
        numbers[nums[i]] = i;
    }
    
    unsigned long long int S1;
    unsigned long long int N1 = 0;
    std::string n1;
    cin >> S1;
    cin.ignore();
    for (unsigned long long int i = 0; i < S1; i++)
    {
        string num1Line;
        cin >> num1Line;
        cin.ignore();
        n1 += num1Line;
        if (1 + i % H == H)
        {
            std::map<std::string, unsigned long long int>::const_iterator ni1 = numbers.find(n1);
            if (numbers.end() == ni1)
            {
                cerr << "Unknown number " << n1 << endl;
                return -1;
            }
            N1 = 20*N1 + ni1->second;
            cerr << "IR: " << N1 << endl;
            n1 = "";
        }
    }
    cerr << "First number is " << N1 << endl;
    
    unsigned long long int S2;
    unsigned long long int N2 = 0;
    std::string n2;
    cin >> S2;
    cin.ignore();
    for (unsigned long long int i = 0; i < S2; i++)
    {
        string num2Line;
        cin >> num2Line;
        cin.ignore();
        n2 += num2Line;
        if (1 + i % H == H)
        {
            std::map<std::string, unsigned long long int>::const_iterator ni2 = numbers.find(n2);
            if (numbers.end() == ni2)
            {
                cerr << "Unknown number " << n2 << endl;
                return -1;
            }
            N2 = 20*N2 + ni2->second;
            n2 = "";
        }
    }
    cerr << "Second number is " << N2 << endl;
    
    string operation;
    cin >> operation;
    cin.ignore();
    
    unsigned long long int result;
    switch (operation[0])
    {
        case '+':
            result = N1 + N2;
            break;
            
        case '-':
            result = N1 - N2;
            break;
            
        case '*':
            result = N1*N2;
            break;
            
        case '/':
            result = N1/N2;
            break;
            
        default:
            cerr << "Unknown operation" << endl;
            return -3;
    }
    
    std::list<std::string> r;
    do
    {
        cerr << result % 20;
        r.push_front(nums[result % 20]);
        result /= 20;
    } while (0 < result);
    cerr << endl;
    
    for (std::list<std::string>::const_iterator i = r.begin(); i != r.end(); i++)
    {
        cerr << *i << endl;
        print_number(*i, H);
    }
}
