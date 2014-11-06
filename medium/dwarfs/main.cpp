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
#include <set>

#include <assert.h>

using namespace std;

int solution(std::set<int>& nodes, std::map<int, std::list<int> >& inc, std::map<int, std::list<int> >& r_inc)
{
    std::map<int, int> n;
    std::list<int> starts;
    
    for (std::set<int>::const_iterator i = nodes.begin(); i != nodes.end(); i++)
    {
        if (r_inc[*i].empty())
        {
            starts.push_back(*i);
            n[*i] = 1;
        }
    }
    
    std::list<int>::const_iterator k = starts.begin();
    assert(starts.end() != k);
    while (starts.end() != k)
    {
        cerr << "process " << *k << endl;
        std::list<int> l = inc[*k];
        for (std::list<int>::const_iterator j = l.begin(); j != l.end(); j++)
        {
            if (0 == n[*j])
            {
                starts.push_back(*j);
            }
            n[*j] = std::max(n[*j], n[*k] + 1);
        }
        k++;
    }
    
    int max = 0;
    for (std::map<int, int>::const_iterator i = n.begin(); i != n.end(); i++)
    {
        if (i->second > max)
        {
            max = i->second;
        }
    }
    return max;
}

int main()
{
    int N;
    cin >> N;
    cin.ignore();
    
    std::map<int, std::list<int> > inc;
    std::map<int, std::list<int> > r_inc;
    std::set<int> nodes;
    for (int i = 0; i < N; i++)
    {
        int X;
        int Y;
        cin >> X >> Y;
        cin.ignore();
        
        nodes.insert(X);
        nodes.insert(Y);
        inc[X].push_back(Y);
        r_inc[Y].push_back(X);
    }

    // Write an action using cout. DON'T FORGET THE "<< endl"
    // To debug: cerr << "Debug messages..." << endl;

    cout << solution(nodes, inc, r_inc) << endl;
}
