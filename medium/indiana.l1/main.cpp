/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int W; // number of columns.
    int H; // number of rows.
    cin >> W >> H;
    cin.ignore();
    
    typedef std::vector<std::vector<int> > field_t;
    field_t field(H);   // [y, x]
    for (int i = 0; i < H; i++)
    {
        field[i].resize(W);
        for (int j = 0; j < W; j++)
        {
            int type;
            std::cin >> type;
            std::cerr << type << " ";
            field[i][j] = type;
        }
        std::cerr << std::endl;
        std::cin.ignore();
    }
    int EX; // the coordinate along the X axis of the exit (not useful for this first mission, but must be read).
    cin >> EX; cin.ignore();

    // game loop
    while (1) {
        int XI;
        int YI;
        string POS;
        cin >> XI >> YI >> POS; cin.ignore();
        
        int pos;
        if (string("LEFT") == POS)
        {
            pos = -1;
        } else if (string("TOP") == POS)
        {
            pos = 0;
        } else if (string("RIGHT") == POS)
        {
            pos = 1;
        } else
        {
            std::cerr << "Invalid position" << std::endl;
            return 1;
        }
        
        switch (field[YI][XI])
        {
            case 0:
                std::cerr << "Wrong logic" << std::endl;
                return 2;
                break;
                
            case 1:
            case 3:
            case 7:
            case 8:
            case 9:
                YI++;
                break;
                
            case 2:
            case 6:
                if (0 == pos)
                {
                    std::cerr << "Wrong position in current context" << std::endl;
                    return 5;
                }
                XI -= pos;
                break;
                
            case 4:
            case 10:
            case 12:
                if (0 == pos)
                {
                    XI--;
                } else if (1 == pos)
                {
                    YI++;
                } else
                {
                    std::cerr << "Wrong position in current context" << std::endl;
                    return 3;
                }
                break;
                
            case 5:
            case 11:
            case 13:
                if (0 == pos)
                {
                    XI++;
                } else if (-1 == pos)
                {
                    YI++;
                } else
                {
                    std::cerr << "Wrong position in current context" << std::endl;
                    return 4;
                }
                break;
        }

        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;

        cout << XI << " " << YI << endl; // One line containing the X Y coordinates of the room in which you believe Indy will be on the next turn.
    }
}
