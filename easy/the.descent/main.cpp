/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <map>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int last_sy = 100500;
    // game loop
    bool discharged = false;
    while (1)
    {
        int SX;
        int SY;
        cin >> SX >> SY;
        cin.ignore();

        typedef std::map<int, int> mountains_t;
        std::map<int, int> mountains;
        for (int i = 0; i < 8; i++)
        {
            int MH; // represents the height of one mountain, from 9 to 0. Mountain heights are provided from left to right.
            cin >> MH;
            cin.ignore();
            
            std::cerr << i << ": " << MH << std::endl;
            mountains[MH] = i;
        }
        
        if (last_sy != SY)
        {
            discharged = false;
        }

        if (!discharged)
        {
            mountains_t::const_reverse_iterator m = mountains.rbegin();
            if (m != mountains.rend())
            {
                std::cerr << "Highest mountain is " << m->second << std::endl;
            }
            if (m != mountains.rend() && m->second == SX)
            {
                std::cout << "FIRE" << std::endl;
                discharged = true;
            } else
            {
                std::cout << "HOLD" << std::endl;
            }
        } else
        {
            std::cout << "HOLD" << std::endl;
        }
    }
}
