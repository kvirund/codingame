/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

int sign(int a)
{
    return a > 0 ? 1 : (a < 0 ? -1 : 0);
}

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int LX; // the X position of the light of power
    int LY; // the Y position of the light of power
    int TX; // Thor's starting X position
    int TY; // Thor's starting Y position
    cin >> LX >> LY >> TX >> TY; cin.ignore();

    // game loop
    while (1)
    {
        int E; // The level of Thor's remaining energy, representing the number of moves he can still make.
        cin >> E;
        cin.ignore();

        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;
        int dx = LX - TX;
        int dy = LY - TY;
        std::string turn;
        if (0 > dy)
        {
            turn += "N";
        } else if (0 < dy)
        {
            turn += "S";
        }
        if (0 < dx)
        {
            turn += "E";
        } else if (0 > dx)
        {
            turn += "W";
        }
        TX += sign(dx);
        TY += sign(dy);
        std::cerr << "dx = " << dx << ", dy =" << dy << std::endl;

        cout << turn << endl; // A single line providing the move to be made: N NE E SE S SW W or NW
    }
}
