/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <map>
#include <set>

using namespace std;

int main()
{
    int N;
    cin >> N;
    cin.ignore();
    
    int C;
    cin >> C;
    cin.ignore();
    
    // budget to pos
    typedef std::multimap<int, int> budget_t;
    budget_t b;
    for (int i = 0; i < N; i++)
    {
        int B;
        cin >> B;
        cin.ignore();
        b.insert(std::pair<int, int>(B, i));
    }
    
    int sum = C;
    int count = N;
    int each = sum/count;
    std::multimap<int, int> pays;
    for (budget_t::const_iterator i = b.begin(); i != b.end(); i++)
    {
        int paid;
        if (i->first < each)
        {
            paid = i->first;
        } else
        {
            paid = each;
        }
        cerr << i->second << ": " << paid << "; ";
        count--;
        sum -= paid;
        if (0 < count)
        {
            each = sum/count;
        }
        pays.insert(std::pair<int, int>(paid, 0));
    }
    cerr << endl;

    if (0 < sum)
    {
        cout << "IMPOSSIBLE" << endl;
    } else
    {
        for (std::multimap<int, int>::const_iterator i = pays.begin(); i != pays.end(); i++)
        {
            cout << i->first << endl;
        }
    }
}
