/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <list>

using namespace std;

std::list<int> mutate(const std::list<int>& line)
{
    std::list<int> result;
    
    int n = -1;
    int count = 0;
    for (std::list<int>::const_iterator i = line.begin(); i != line.end(); i++)
    {
        if (-1 == n)
        {
            n = *i;
            count = 1;
        } else if (*i != n)
        {
            result.push_back(count);
            result.push_back(n);
            n = *i;
            count = 1;
        } else if (*i == n)
        {
            count++;
        }
    }
    if (-1 != n)
    {
        result.push_back(count);
        result.push_back(n);
    }
    
    return result;
}

int main()
{
    int R;
    cin >> R; cin.ignore();
    int L;
    cin >> L; cin.ignore();
    
    std::list<int> line;
    line.push_back(R);
    
    for (int i = 1; i < L; i++)
    {
        line = mutate(line);
    }

    // Write an action using cout. DON'T FORGET THE "<< endl"
    // To debug: cerr << "Debug messages..." << endl;

    bool first = true;
    for (std::list<int>::const_iterator i = line.begin(); i != line.end(); i++)
    {
        if (!first)
        {
            cout << " ";
        }
        cout << *i;
        first = false;
    }
}
