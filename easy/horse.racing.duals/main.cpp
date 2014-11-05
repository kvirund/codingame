/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
// Read inputs from stdin. Write outputs to stdout.

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <cstdlib>

using namespace std;

int main()
{
	int n;
	cin >> n;
	
	std::map<int, int> helper;
	std::vector<int> strenght(n);
	for (int i = 0; i < n; i++)
	{
	    int s;
		cin >> s;
		cin.ignore();
		helper[s] = i;
	}
	
	int j = 0;
	for (std::map<int, int>::const_iterator i = helper.begin(); i != helper.end(); i++)
	{
	    std::cerr << i->second << ", " << i->first << std::endl;
	    strenght[j++] = i->first;
	}

    int min = 100500;
	for (size_t i = 1; i < strenght.size(); i++)
	{
	    std::cerr << "i = " << i << ", " << strenght[i] << " - " << strenght[i - 1] << std::endl;
	    if (min > abs(strenght[i] - strenght[i - 1]))
	    {
	        min = abs(strenght[i] - strenght[i - 1]);
	    }
	}
	
	std::cout << min << std::endl;
	
	return 0;
}
