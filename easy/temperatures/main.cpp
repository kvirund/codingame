/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
// Read inputs from stdin. Write outputs to stdout.

#include <iostream>
#include <string>
#include <map>
#include <cstdlib>

int main()
{
	int n;
    std::cin >> n;
    std::cin.ignore();
	std::cerr << "n == " << n << std::endl;
	
	int v;
	int min = -1;
	int mvalue = 100500;
	for (int i = 1; i <= n; i++)
	{
        std::cin >> v;
		std::cerr << i << ": " << v << " " << std::endl;
		if (abs(v) < abs(mvalue)
		    || (abs(mvalue) == abs(v) && mvalue < 0 && v > 0))
	    {
	        std::cerr << "yes" << std::endl;
	        min = i;
	        mvalue = v;
	    }
	}
	
	if (-1 == min)
	{
	    std::cout << "0" << std::endl;
	} else
	{
	    std::cout << mvalue << std::endl;
	}

	return 0;
}
