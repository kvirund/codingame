/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <list>
#include <cmath>

using namespace std;


const double G = -3.711;

// 68 is arcsin(3.711/4). Angle for which delta of vertical speed will be zero for full thrust
const int TrueAngle = 90 - 68;

typedef std::pair<int, int> point_t;
typedef std::list<point_t> surface_t;
    
struct SVector
{
    int x, y;
    SVector(int _x, int _y): x(_x), y(_y) {}
    SVector(const SVector& v): x(v.x), y(v.y) {}
    SVector& operator=(const SVector& v)
    {
        if (this != &v)
        {
            x = v.x;
            y = v.y;
        }
        return *this;
    }
    
    SVector operator+(const SVector& v) const
    {
        return SVector(x + v.x, y + v.y);
    }
    
    SVector operator-(const SVector& v) const
    {
        return SVector(x - v.x, y - v.y);
    }
    
    int modulus() const
    {
        return int(sqrt(x*x + y*y));
    }
};

int X;
int Y;
int HS; // the horizontal speed (in m/s), can be negative.
int VS; // the vertical speed (in m/s), can be negative.
int R; // the rotation angle in degrees (-90 to 90).
point_t landing_area(0, 0);

void move_right(int& angle, int& thrust, int vdistance, int dhs = 30)
{
    int desired = dhs < HS ? 0 : -TrueAngle;
    angle = R + std::max(std::min(desired - R, 15), -15);
    std::cerr << desired << "/" << R << "/" << angle << std::endl;
    if (0 != desired)
    {
        thrust = 4;
    }
    else
    {
        thrust = (500 < vdistance ? -20 : 0) > VS ? 4 : 2;
    }
}

void move_left(int& angle, int& thrust, int vdistance, int dhs = -30)
{
    int desired = dhs > HS ? 0 : TrueAngle;
    angle = R + std::max(std::min(desired - R, 15), -15);
    std::cerr << desired << "/" << R << "/" << angle << std::endl;
    if (0 != desired)
    {
        thrust = 4;
    }
    else
    {
        thrust = (500 < vdistance ? -20 : 0) > VS ? 4 : 2;
    }
}

void stop(int& angle, int& thrust, int vdistance)
{
    angle = 0;
    if (0 < HS)
    {
        // left normalization
        move_left(angle, thrust, vdistance, -5);
    }
    else if (0 > HS)
    {
        // right normalization
        move_right(angle, thrust, vdistance, 5);
    }
    else
    {
        thrust = -30 > VS ? 4 : 0;
    }
}

int main()
{
    int N; // the number of points used to draw the surface of Mars.
    cin >> N;
    cin.ignore();
    
    int la_length = 0;
    surface_t surface;
    for (int i = 0; i < N; i++)
    {
        int LAND_X; // X coordinate of a surface point. (0 to 6999)
        int LAND_Y; // Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
        cin >> LAND_X >> LAND_Y;
        cin.ignore();
        if (!surface.empty()
            && surface.back().second == LAND_Y)
        {
            landing_area = surface.back();
            la_length = LAND_X - landing_area.first;
        }
        surface.push_back(point_t(LAND_X, LAND_Y));
    }

    // game loop
    while (1)
    {
        int F; // the quantity of remaining fuel in liters.
        int P; // the thrust power (0 to 4).
        cin >> X >> Y >> HS >> VS >> F >> R >> P; cin.ignore();
        
        SVector ML(X, Y);
        SVector D(HS, VS);
        SVector LZ_L(landing_area.first, landing_area.second);
        SVector LZ_R(landing_area.first + la_length, landing_area.second);
        SVector LZ_M(landing_area.first + la_length/2, landing_area.second);
        SVector A = LZ_M - ML;
//        SVector T
        
        int angle = 0;
        int thrust = 0;
        
        int vdistance = Y - landing_area.second;
        if (40 < HS)
        {
            move_left(angle, thrust, vdistance);
        }
        else if (-40 > HS)
        {
            move_right(angle, thrust, vdistance);
        }
        else
        {
            int direction = X < landing_area.first ? 1 : (X > landing_area.first + la_length ? -1 : 0);
            std::cerr << "direction: " << (-1 == direction ? "left" : (0 == direction ? "down" : "right")) << std::endl;
            switch (direction)
            {
                case -1:
                    move_left(angle, thrust, vdistance);
                    break;
                
                case 0:
                    stop(angle, thrust, vdistance);
                    break;
                    
                case 1:
                    move_right(angle, thrust, vdistance);
                    break;
            }
        }
        
        cout << angle << " " << thrust << endl; // R P. R is the desired rotation angle. P is the desired thrust power.
    }
}
