/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <list>

using namespace std;

void pad(int step)
{
    for (int i = 0; i < step; i++)
    {
        std::cout << " ";
    }
}

bool find_solution(int step, int R, int G, int L, int S, int X, bool jumped, std::list<std::string>& solution)
{
    //pad(step);
    //std::cerr << "step #" << step + 1 << std::endl;

    if ((X < R + G && X >= R)   // In down
        || X >= R + G + L       // Out of range
        || S < 0)               // Speed is negative
    {
        return false;
    }
    if (0 == S && R + G + L > X && X > R + G && jumped)
    {
        return true;
    }

    if (((0 < S && G + 1 < S) || jumped)
            && !(X < R && X + S - 1 > R + G))
    {
        //pad(step);
        //std::cerr << "Try SLOW: R == " << R << "; G == " << G << "; L == " << L << "; S == " << S << "; X == " << X << "; " << (jumped ? "already jumped" : "not jumped yet") << std::endl;
        if (find_solution(step + 1, R, G, L, S - 1, X + S - 1, jumped, solution))
        {
            solution.push_front("SLOW");
            std::cerr << "SLOW" << std::endl;
            return true;
        }
    }
    if (0 != S
            && !(X < R && X + S >= R + G))
    {
        //pad(step);
        //std::cerr << "Try WAIT: R == " << R << "; G == " << G << "; L == " << L << "; S == " << S << "; X == " << X << "; " << (jumped ? "already jumped" : "not jumped yet") << std::endl;
        if (find_solution(step + 1, R, G, L, S, X + S, jumped, solution))
        {
            solution.push_front("WAIT");
            std::cerr << "WAIT" << std::endl;
            return true;
        }
    }
    if (G + 1 > S
            && !(X < R && X + S + 1 >= R + G))
    {
        //pad(step);
        //std::cerr << "Try SPEED: R == " << R << "; G == " << G << "; L == " << L << "; S == " << S << "; X == " << X << "; " << (jumped ? "already jumped" : "not jumped yet") << std::endl;
        if (find_solution(step + 1, R, G, L, S + 1, X + S + 1, jumped, solution))
        {
            solution.push_front("SPEED");
            std::cerr << "SPEED" << std::endl;
            return true;
        }
    }
    if (0 < S
            && R - 1 == X)      // Try JUMP
    {
        //pad(step);
        //std::cerr << "Try JUMP: R == " << R << "; G == " << G << "; L == " << L << "; S == " << S << "; X == " << X << "; " << (jumped ? "already jumped" : "not jumped yet") << std::endl;
        if (find_solution(step + 1, R, G, L, S, X + S, true, solution))
        {
            solution.push_front("JUMP");
            std::cerr << "JUMP" << std::endl;
            return true;
        }
    }
    return false;
}

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int R; // the length of the road before the gap.
    cin >> R; cin.ignore();
    int G; // the length of the gap.
    cin >> G; cin.ignore();
    int L; // the length of the landing platform.
    cin >> L; cin.ignore();

    bool solution_found = false;
    std::list<std::string> solution;
    // game loop
    while (1)
    {
        int S; // the motorbike's speed.
        cin >> S; cin.ignore();
        int X; // the position on the road of the motorbike.
        cin >> X; cin.ignore();

        std::cerr << R << " " << G << " " << L << std::endl;
        std::cerr << S << " " << X << std::endl;
        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;

        if (!solution_found)
        {
            bool result = find_solution(0, R, G, L, S, X, false, solution);
            if (!result)
            {
                std::cerr << "No solution found" << std::endl;
            }
        } else if (solution.empty())
        {
            std::cout << "Solution is empty" << std::endl;
        }

        std::cout << solution.front() << std::endl;
        solution.pop_front();
    }
}

