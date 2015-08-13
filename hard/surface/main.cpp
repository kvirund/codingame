/**
 * \author Anton Gorev aka Veei
 * \date 2015-08-09
 */
#include <iostream>
#include <string>
#include <map>
#include <list>

#include <assert.h>

int main()
{
	int W;
	int H;
	std::cin >> W;
	std::cin.ignore();
	std::cin >> H;
	std::cin.ignore();

typedef std::pair<int, int> pos_t;
    int surf[W][H];
	for (int i = 0; i < H; i++)
	{
	    std::string row;
	    std::getline(std::cin, row);
	    assert(static_cast<size_t>(W) == row.length());
	    int l = row.length();
	    for (int j = 0; j < l; j++)
	    {
	        if ('O' == row[j])
	        {
	            surf[j][i] = -1;
	        }
	        else
	        {
	            surf[j][i] = 0;
	        }
	    }
	}
	
    // Tests
    int N;
    std::cin >> N;
    std::cin.ignore();
	for (int i = 0; i < N; i++)
	{
	    int X;
	    int Y;
	    std::cin >> X >> Y;
	    std::cin.ignore();
	    
	    int result;
	    if (-1 == surf[X][Y])
	    {
	        // Fill
	        result = 0;
	        std::list<pos_t> to_process;
	        std::list<pos_t> lake;
	        
	        to_process.push_back(pos_t(X, Y));
	        while (!to_process.empty())
	        {
	            const pos_t p = to_process.front();
	            to_process.pop_front();
	            if (-1 == surf[p.first][p.second])
	            {
	                result++;
	                surf[p.first][p.second] = result;
	                lake.push_back(p);
	                
	                if (0 < p.first)
	                {
	                    to_process.push_back(pos_t(p.first - 1, p.second));
	                }
	                if (0 < p.second)
	                {
	                    to_process.push_back(pos_t(p.first, p.second - 1));
	                }
	                if (p.first < W - 1)
	                {
	                    to_process.push_back(pos_t(p.first + 1, p.second));
	                }
	                if (p.second < H - 1)
	                {
	                    to_process.push_back(pos_t(p.first, p.second + 1));
	                }
	            }
	        }
	        
	        while (!lake.empty())
	        {
	            const pos_t p = lake.front();
	            surf[p.first][p.second] = result;
	            lake.pop_front();
	        }
	    }
	    else
	    {
	        result = surf[X][Y];
	    }
	    std::cout << result << std::endl;
	}

	return 0;
}
