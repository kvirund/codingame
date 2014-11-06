/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#include <assert.h>

int R; // number of rows.
int C; // number of columns.
int A; // number of rounds between the time the alarm countdown is activated and the time the alarm goes off.

enum ECell
{
    EC_WALL = '#',
    EC_HOLLOW = '.',
    EC_START = 'T',
    EC_CONTROL = 'C',
    EC_UNKNOWN = '?'
};

typedef std::vector<int> wrow_t;
typedef std::vector<wrow_t> way_t;
typedef std::vector<ECell> row_t;
typedef std::vector<row_t> field_t;
typedef std::pair<int, int> pos_t;

std::string step(const field_t& f, const pos_t& s, bool& back, bool& explore)
{
    bool step_taken;
    bool found_way = false;
    way_t ways(R, wrow_t(C, 0));
    ways[s.first][s.second] = 1;
    pos_t e(-1, -1);
    pos_t c(-1, -1);
    do
    {
        step_taken = false;
        way_t wc = ways; 
        for (int y = 0; y < R; y++)
        {
            for (int x = 0; x < C; x++)
            {
                if (0 == ways[y][x]
                    && (EC_HOLLOW == f[y][x]
                        || EC_CONTROL == f[y][x]
                        || EC_START == f[y][x]
                        || EC_UNKNOWN == f[y][x]))
                {
                    if (0 < y && 0 < ways[y - 1][x])
                    {
                        wc[y][x] = 1;
                        step_taken = true;
                    }
                    if (R > y + 1 && 0 < ways[y + 1][x])
                    {
                        wc[y][x] = 1;
                        step_taken = true;
                    }
                    if (0 < x && 0 < ways[y][x - 1])
                    {
                        wc[y][x] = 1;
                        step_taken = true;
                    }
                    if (C > x + 1 && 0 < ways[y][x + 1])
                    {
                        wc[y][x] = 1;
                        step_taken = true;
                    }
                    if (1 == wc[y][x])
                    {
                        if (back)
                        {
                            if (EC_START == f[y][x])
                            {
                                found_way = true;
                                e = pos_t(y, x);
                            }
                        }
                        else
                        {
                            if (EC_CONTROL == f[y][x])
                            {
                                c = pos_t(y, x);
                            }
                            if (explore && EC_UNKNOWN == f[y][x])
                            {
                                found_way = true;
                                e = pos_t(y, x);
                                std::cerr << "move to " << y << ", " << x << std::endl;
                            }
                        }
                    }
                } else if (0 < ways[y][x])
                {
                    wc[y][x] = 1 + ways[y][x];
                }
            }
        }
        ways = wc;
    } while (step_taken && !found_way);
    
    if (!found_way && explore)
    {
        explore = false;
    }
    
    if (!explore && !back)
    {
        e = c;
    }
    
    for (int y = 0; y < R; y++)
    {
        for (int x = 0; x < C; x++)
        {
            std::cerr.width(3);
            std::cerr << ways[y][x];
        }
        std::cerr << std::endl;
    }

    assert(-1 != e.first);
    
    bool last_step = true;
    while (1 < abs(e.first - s.first) + abs(e.second - s.second))
    {
        //std::cerr << e.first << ", " << e.second << std::endl;
        if (0 < e.first && ways[e.first][e.second] < ways[e.first - 1][e.second])
        {
            e.first--;
        }
        else if (R > e.first + 1 && ways[e.first][e.second] < ways[e.first + 1][e.second])
        {
            e.first++;
        }
        else if (0 < e.second && ways[e.first][e.second] < ways[e.first][e.second - 1])
        {
            e.second--;
        }
        else if (C > e.second + 1 && ways[e.first][e.second] < ways[e.first][e.second + 1])
        {
            e.second++;
        }
        else
        {
            assert(false);
        }
        last_step = false;
    }
    
    if (last_step)
    {
        back = true;
    }
    if (e.first < s.first)
    {
        return "UP";
    } else if (e.first > s.first)
    {
        return "DOWN";
    } else if (e.second < s.second)
    {
        return "LEFT";
    } else if (e.second > s.second)
    {
        return "RIGHT";
    }
    
    assert(false);
}

int main()
{
    std::cin >> R >> C >> A;
    std::cin.ignore();

    pos_t start(-1, -1);
    bool first_step = true;
    
    field_t field(R, row_t(C, EC_UNKNOWN));
    bool back = false;
    // game loop
    while (1)
    {
        int KR; // row where Kirk is located.
        int KC; // column where Kirk is located.
        std::cin >> KR >> KC;
        std::cin.ignore();
        
        pos_t pos(KR, KC);
        pos_t end;

        for (int i = 0; i < R; i++)
        {
            std::string ROW; // C of the characters in '#.TC?' (i.e. one line of the ASCII maze).
            std::cin >> ROW;
            std::cin.ignore();
            
            std::cerr << ROW << std::endl;
            for (size_t j = 0; j < C; j++)
            {
                field[i][j] = static_cast<ECell>(ROW[j]);
                if (EC_START == ROW[j])
                {
                    if (first_step)
                    {
                        start = pos;
                        first_step = false;
                    }
                }
            }
        }
        
        bool explore = true;
        std::cout << step(field, pos, back, explore) << std::endl;
    }
}
