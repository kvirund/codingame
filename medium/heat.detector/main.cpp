#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>

using namespace std;

class CRectangle
{
    int m_l;
    int m_t;
    int m_r;
    int m_b;
    
    public:
        CRectangle(int l, int t, int w, int h): m_l(l), m_t(t), m_r(l + w), m_b(t + h) {}
        
        void turn(int& x, int& y, int vertical, int horizontal)
        {
            std::cerr << "L: " << m_l << "; R: " << m_r << "; T: " << m_t << "; B: " << m_b << std::endl;
            std::cerr << "X: " << x << "; Y: " << y << std::endl;
            switch (horizontal)
            {
                case 0:
                    m_l = m_r = x;
                    break;
                    
                case 1:
                    m_l = x;
                    break;
                    
                case -1:
                    m_r = x;
                    break;
                    
                default:
                    std::cerr << "Invalid parameters" << std::endl;
                    throw std::runtime_error("fuck");
            }
            
            switch (vertical)
            {
                case 0:
                    m_t = m_b = y;
                    break;
                    
                case 1:
                    m_t = y;
                    break;
                    
                case -1:
                    m_b = y;
                    break;
                    
                default:
                    std::cerr << "Invalid parameters" << std::endl;
                    throw std::runtime_error("fuck");
            }
            
            std::cerr << "L: " << m_l << "; R: " << m_r << "; T: " << m_t << "; B: " << m_b << std::endl;
            x = m_l + (m_r - m_l) / 2;
            y = m_t + (m_b - m_t) / 2;
        }
};

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int W; // width of the building.
    int H; // height of the building.
    cin >> W >> H; cin.ignore();
    int N; // maximum number of turns before game over.
    cin >> N; cin.ignore();
    int X0;
    int Y0;
    cin >> X0 >> Y0; cin.ignore();
    CRectangle area(0, 0, W, H);

    // game loop
    while (1)
    {
        string BOMB_DIR; // the direction of the bombs from batman's current location (U, UR, R, DR, D, DL, L or UL)
        cin >> BOMB_DIR;
        cin.ignore();
        
        int horizontal;
        int vertical;
        if (string("U") == BOMB_DIR)
        {
            horizontal = 0;
            vertical = -1;
        } else if (string("UR") == BOMB_DIR)
        {
            horizontal = 1;
            vertical = -1;
        } else if (string("R") == BOMB_DIR)
        {
            horizontal = 1;
            vertical = 0;
        } else if (string("DR") == BOMB_DIR)
        {
            horizontal = vertical = 1;
        } else if (string("D") == BOMB_DIR)
        {
            horizontal = 0;
            vertical = 1;
        } else if (string("DL") == BOMB_DIR)
        {
            horizontal = -1;
            vertical = 1;
        } else if (string("L") == BOMB_DIR)
        {
            horizontal = -1;
            vertical = 0;
        } else if (string("UL") == BOMB_DIR)
        {
            horizontal = vertical = -1;
        } else
        {
            std::cerr << "Wrong direction" << std::endl;
        }
        
        std::cerr << BOMB_DIR <<  "; V: " << vertical << "; H: " << horizontal << std::endl;
        area.turn(X0, Y0, vertical, horizontal);

        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;

        cout << X0 << " " << Y0 << endl; // the location of the next window Batman should jump to.
    }
}
