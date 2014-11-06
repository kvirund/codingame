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
    int nbFloors; // number of floors
    int width; // width of the area
    int nbRounds; // maximum number of rounds
    int exitFloor; // floor on which the exit is found
    int exitPos; // position of the exit on its floor
    int nbTotalClones; // number of generated clones
    int nbAdditionalElevators; // ignore (always zero)
    int nbElevators; // number of elevators
    cin >> nbFloors >> width >> nbRounds >> exitFloor >> exitPos >> nbTotalClones >> nbAdditionalElevators >> nbElevators; cin.ignore();
    
    typedef std::pair<int, int> pair_t;
    typedef std::vector<int> elevators_t;
    typedef std::vector<bool> fixed_t;
    
    elevators_t e(nbElevators + 1);
    fixed_t f(nbElevators, false);
    for (int i = 0; i < nbElevators; i++)
    {
        int elevatorFloor; // floor on which this elevator is found
        int elevatorPos; // position of the elevator on its floor
        cin >> elevatorFloor >> elevatorPos;
        cin.ignore();
        e[elevatorFloor] = elevatorPos;
    }
    e[nbElevators] = exitPos;
    
    bool first = true;
    int start = -1;
    while (1)
    {
        int cloneFloor; // floor of the leading clone
        int clonePos; // position of the leading clone on its floor
        string direction; // direction of the leading clone: LEFT or RIGHT
        cin >> cloneFloor >> clonePos >> direction; cin.ignore();

        if (-1 == cloneFloor || f[cloneFloor])
        {
            cout << "WAIT" << endl;
            continue;
        }
        if (first)
        {
            start = clonePos;
            first = false;
        }
        
        cerr << cloneFloor << "/" << e.size() << endl;
        if ((clonePos < e[cloneFloor] && direction == "RIGHT")
            || (clonePos > e[cloneFloor] && direction == "LEFT"))
        {
            cout << "WAIT" << endl;
            f[cloneFloor] = true;
        } else
        {
            if ((0 < cloneFloor && clonePos != e[cloneFloor - 1])
                || (0 == cloneFloor && clonePos != start))
            {
                cout << "BLOCK" << endl;
            }
            else
            {
                cout << "WAIT" << endl;
            }
        }
    }
}
