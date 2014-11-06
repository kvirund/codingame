/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <map>
#include <string.h>
#include <list>

using namespace std;

struct SWeight
{
    int weight;
    const char *letters;
};

SWeight weights[] = {
    {1,  "eaionrtlsu"},
    {2,  "dg"},
    {3,  "bcmp"},
    {4,  "fhvwy"},
    {5,  "k"},
    {8,  "jx"},
    {10, "qz"},
};
std::map<char, int> l;

bool test_word(const std::string& w, const std::string& letters, int& score)
{
    std::map<char, int> c;
    for (int i = 0; i < letters.length(); i++)
    {
        c[letters[i]]++;
    }
    
    for (std::map<char, int>::const_iterator i = c.begin(); i != c.end(); i++)
    {
        //cerr << i->first << ": " << i->second << endl;
    }

    score = 0;
    for (int i = 0; i < w.length(); i++)
    {
        if (0 < c[w[i]]--)
        {
            cerr << w[i] << " is " << l[w[i]] << endl;
            score += l[w[i]];
        } else
        {
            cerr << w[i] << endl;
            return false;
        }
    }
    
    return true;
}

int main()
{
    for (int i = 0; i < sizeof(weights)/sizeof(weights[0]); i++)
    {
        int wl = strlen(weights[i].letters);
        for (int j = 0; j < wl; j++)
        {
            l[weights[i].letters[j]] = weights[i].weight;
            //cerr << weights[i].weight << weights[i].letters[j] << endl;
        }
    }
    
    int N;
    cin >> N;
    cin.ignore();
    
    std::list<std::string> words;
    for (int i = 0; i < N; i++)
    {
        string W;
        getline(cin, W);
        words.push_back(W);
    }
    string LETTERS;
    getline(cin, LETTERS);
    cerr << LETTERS << endl;
    
    int max = 0;
    std::string r = "";
    for (std::list<std::string>::const_iterator i = words.begin(); i != words.end(); i++)
    {
        int s;
        if (test_word(*i, LETTERS, s))
        {
            cerr << *i << ": " << s << endl;
            if (max < s)
            {
                max = s;
                r = *i;
            }
        }
    }

    // Write an action using cout. DON'T FORGET THE "<< endl"
    // To debug: cerr << "Debug messages..." << endl;

    cout << r << endl;
}
