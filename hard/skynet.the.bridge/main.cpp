/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <list>

using namespace std;

int V; // the minimum amount of motorbikes that must survive

typedef std::list<std::string> solution_t;
typedef std::vector<std::string> lanes_t;
lanes_t lanes(4);

struct SBikes
{
    int s;
    int c;
    std::vector<int> x;
    std::vector<int> y;
    std::vector<bool> a;

    SBikes(int count): s(0), c(count), x(count, 0), y(count, 0), a(count, false) {}
    SBikes(const SBikes& from): s(from.s), c(from.c), x(from.x), y(from.y), a(from.a) {}

    int count() const
    {
        int C = 0;
        for (int i = 0; i < c; i++)
        {
            if (a[i])
            {
                C++;
            }
        }
        return C;
    }
    bool have_bikes(int N) const
    {
        return N <= count();
    }

    void up()
    {
        for (int i = 0; i < c; i++)
        {
            if (a[i])
            {
                if (0 == y[i])
                {
                    a[i] = false;
                }
                else
                {
                    y[i]--;
                }
            }
        }
    }
    void down()
    {
        for (int i = 0; i < c; i++)
        {
            if (a[i])
            {
                if (3 == y[i])
                {
                    a[i] = false;
                }
                else
                {
                    y[i]++;
                }
            }
        }
    }
};

void indent_(int c)
{
    for (int i = 0; i < c; i++)
    {
        std::cerr << " ";
    }
}

bool solve(SBikes b, solution_t& result, const std::string& action = "", int indent = 0)
{
    bool solved = false;

    do
    {
        int ll = static_cast<int>(lanes[0].length());
        if (!action.empty())
        {
            // check for at least V bikes was not broken
            if (!b.have_bikes(V))
            {
                indent_(indent);
                std::cerr << "not enough bikes: " << b.count() << " from " << V << std::endl;
                break;
            }

            indent_(indent);
            std::cerr << action << ": X is " << b.x[0] << "; speed is " << b.s << "; lane length is " << ll << std::endl;
            if (!(ll > b.x[0]))
            {
                solved = true;
                break;
            }

            // make changes according to the action
            if (action == "SPEED")
            {
                b.s++;
            }
            else if (action == "SLOW")
            {
                if (0 == b.s)
                {
                    break;
                }
                b.s--;
            }
            else if (action == "UP")
            {
                b.up();
            }
            else if (action == "DOWN")
            {
                b.down();
            }

            // model moving
            for (int i = 0; i < b.c; i++)
            {
                if (b.a[i])
                {
                    if (action != "JUMP")
                    {
                        for (int j = b.x[i] + 1; j <= std::min<int>(b.x[i] + b.s, ll - 1); j++)
                        {
                            if ('0' == lanes[b.y[i]][j])
                            {
                                indent_(indent);
                                std::cerr << "bike has been broken at position " << j << std::endl;
                                b.a[i] = false;
                            }
                        }
                        if (action == "UP")
                        {
                            for (int j = b.x[i] + 1; j <= std::min<int>(b.x[i] + b.s - 1, ll - 1); j++)
                            {
                                if ('0' == lanes[b.y[i] + 1][j])
                                {
                                    indent_(indent);
                                    std::cerr << "bike has been broken at position " << j << std::endl;
                                    b.a[i] = false;
                                }
                            }
                        }
                        else if (action == "DOWN")
                        {
                            for (int j = b.x[i] + 1; j <= std::min<int>(b.x[i] + b.s - 1, ll - 1); j++)
                            {
                                if ('0' == lanes[b.y[i] - 1][j])
                                {
                                    indent_(indent);
                                    std::cerr << "bike has been broken at position " << j << std::endl;
                                    b.a[i] = false;
                                }
                            }
                        }
                    }
                    else
                    {
                        if ('0' == lanes[b.y[i]][b.x[i] + b.s])
                        {
                            indent_(indent);
                            std::cerr << "bike has jumped into hole at position " << b.x[i] + b.s << std::endl;
                            b.a[i] = false;
                        }
                    }
                }
                b.x[i] += b.s;
            }
        }

        if (ll - b.x[0] > b.s && solve(b, result, "SPEED", indent + 1))
        {
            result.push_front("SPEED");
            solved = true;
            break;
        }
        if (1 < b.s && solve(b, result, "SLOW", indent + 1))
        {
            result.push_front("SLOW");
            solved = true;
            break;
        }
        if (0 < b.s && solve(b, result, "JUMP", indent + 1))
        {
            result.push_front("JUMP");
            solved = true;
            break;
        }
        if (0 < b.s && solve(b, result, "WAIT", indent + 1))
        {
            result.push_front("WAIT");
            solved = true;
            break;
        }
        if (solve(b, result, "UP", indent + 1))
        {
            result.push_front("UP");
            solved = true;
            break;
        }
        if (solve(b, result, "DOWN", indent + 1))
        {
            result.push_front("DOWN");
            solved = true;
            break;
        }
    } while (0);

    return solved;
}

int main()
{
    int M; // the amount of motorbikes to control
    cin >> M;
    cin.ignore();
    cin >> V;
    cin.ignore();
    std::cerr << M << std::endl << V << std::endl;

    // read lanes
    for (int i = 0; i < 4; i++)
    {
        getline(cin, lanes[i]);
    }

    bool first = true;
    SBikes b(M);
    solution_t solution;
    bool solved = false;

    while (1)
    {
        int S; // the motorbikes' speed
        cin >> S;
        cin.ignore();
        std::cerr << S << std::endl;
        if (first)
        {
            b.s = S;
        }

        lanes_t ls = lanes;
        for (int i = 0; i < M; i++)
        {
            int X; // x coordinate of the motorbike
            int Y; // y coordinate of the motorbike
            int A; // indicates whether the motorbike is activated "1" or detroyed "0"
            cin >> X >> Y >> A;
            cin.ignore();
            if (first)
            {
                b.x[i] = X;
                b.y[i] = Y;
                b.a[i] = (1 == A ? true : false);
            }
            if (1 == A)
            {
                ls[Y][X] = '*';
            }
            std::cerr << X << " " << Y << " " << A << std::endl;
        }

        int ll = static_cast<int>(lanes[0].length());
        for (int i = 0; i < ll; i++)
        {
            std::cerr << i % 10;
        }
        std::cerr << std::endl;

        for (int i = 0; i < 4; i++)
        {
            std::cerr << ls[i] << std::endl;
        }

        if (first)
        {
            solved = solve(b, solution);
            first = false;
        }

        if (solved && !solution.empty())
        {
            cout << solution.front() << endl; // A single line containing one of 6 keywords: SPEED, SLOW, JUMP, WAIT, UP, DOWN.
            solution.pop_front();
        }
        else
        {
            std::cerr << "no solution" << std::endl;
            break;
        }
    }
}
