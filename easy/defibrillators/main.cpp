/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
#include <math.h>

#include <iostream>
#include <string>
#include <vector>
#include <cstdio>

using namespace std;

double get_number(std::string& s)
{
    std::string::size_type p = s.find(',');
    if (std::string::npos != p)
    {
        s[p] = '.';
    }
    float result;
    sscanf(s.c_str(), "%f", &result);
    return result;
}

int main()
{
        int count;
        std::string s1, s2;
        double longtitude, latitude;
        getline(cin, s1);
        getline(cin, s2);
        cin >> count;
        cin.ignore();

        longtitude = get_number(s1)*M_PI/180;
        latitude = get_number(s2)*M_PI/180;
        std::cerr << s1 << ": " << longtitude << ", " << s2 << ": " << latitude << ", " << count << std::endl;

        std::string name;
        double min_distance;
        for (int i = 0; i < count; i++)
        {
                std::string line;
                getline(cin, line);

                std::vector<std::string> parts(6);
                for (int i = 0; i < 6 - 1; i++)
                {
                    std::string::size_type pos = line.find(';');
                    if (pos == std::string::npos)
                    {
                        //std::cout << "Invalid format: " << line << std::endl;
                        return -1;
                    }
                    parts[i] = line.substr(0, pos);
                    line = line.substr(pos + 1);
                    //std::cerr << "Part #" << i << ": " << parts[i] << std::endl;
                }
                parts[5] = line;
                //std::cerr << "Part #5: " << parts[5] << std::endl;

                double _long = get_number(parts[4])*M_PI/180;
                double _lat = get_number(parts[5])*M_PI/180;
                double x = (_long - longtitude)*cos((_lat + longtitude)/2);
                double y = _lat - latitude;
                double distance = sqrt(x*x + y*y)*6371;

                if (name.empty()
                    || min_distance > distance)
                {
                    name = parts[1];
                    min_distance = distance;
                }
        }

        std::cout << name << std::endl;

        return 0;
}
