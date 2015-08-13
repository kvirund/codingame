/**
 * \author Anton Gorev aka Veei
 * \date 2015-08-09
 */
#include <iostream>
#include <string>
#include <list>
#include <vector>
#include <algorithm>
#include <iterator>

#include <string.h>

int get_intersection(const std::string& s1, const std::string& s2)
{
    size_t l = s1.length();
    if (std::string::npos != s2.find(s1))
    {
        return l;
    }
    for (size_t i = 0; i < l; i++)
    {
        bool result = true;
        for (size_t j = i; j < l; j++)
        {
            if (s1[j] != s2[j - i])
            {
                result = false;
                break;
            }
        }
        if (result)
        {
            return l - i;
        }
    }
    return 0;
}

int main()
{
	int n;
	std::cin >> n;
	std::cin.ignore();
	
	std::list<std::string> subs;
	for (int i = 0; i < n; i++)
	{
	    std::string sub;
		std::getline(std::cin, sub);
		std::cerr << sub << std::endl;
        subs.push_back(sub);
	}
	
	int j = 0;
	size_t result = 0;
	std::vector<std::string> pieces(subs.size());
	std::vector<int> perm(subs.size());
	for (std::list<std::string>::const_iterator i = subs.begin(); i != subs.end(); i++)
	{
	    perm[j] = j;
	    pieces[j] = *i;
	    result += i->length();
	    j++;
	}

	do
	{
	    copy(perm.begin(), perm.end(), std::ostream_iterator<int>(std::cerr, ", "));
	    std::cerr << std::endl;
	    
	    std::string s = pieces[perm[0]];
	    for (size_t i = 1; i < perm.size(); i++)
	    {
	        int r = get_intersection(s, pieces[perm[i]]);
	        std::cerr << "r is " << r << std::endl;
	        s = s.substr(0, s.length() - r);
	        s += pieces[perm[i]];
	    }
	    std::cerr << s << std::endl;
	    if (result > s.length())
	    {
	        result = s.length();
	    }
	} while (next_permutation(perm.begin(), perm.end()));

    std::cout << result << std::endl;

    return 0;
}
