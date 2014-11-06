/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <set>

using namespace std;

int solve(const std::set<std::string>& numbers)
{
    std::vector<std::string> n(numbers.size());
    int count = 0;
    for (std::set<std::string>::const_iterator i = numbers.begin(); i != numbers.end(); i++)
    {
        n[count++] = *i;
    }
    
    size_t  result = n[0].length();
    size_t pnl = result;
    for (int k = 1; k < count; k++)
    {
        bool tail = false;
        size_t nl = n[k].length();
        for (size_t j = 0; j < nl; j++)
        {
            if (tail)
            {
                result++;
            } else if (j < pnl && n[k - 1][j] == n[k][j])
            {
                // merged node
            } else
            {
                tail = true;
                result++;
            }
        }
        pnl = nl;
    }
    
    return result;
}

int main()
{
    int N;
    cin >> N;
    cin.ignore();
    
    std::set<std::string> numbers;
    for (int i = 0; i < N; i++)
    {
        string telephone;
        cin >> telephone;
        cin.ignore();
        numbers.insert(telephone);
    }
    
    // Write an action using cout. DON'T FORGET THE "<< endl"
    // To debug: cerr << "Debug messages..." << endl;

    cout << solve(numbers) << endl; // The number of elements (referencing a number) stored in the structure.
}
