/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
#include <string.h>

#include <iostream>
#include <string>
#include <vector>
#include <map>

int main()
{
        int width, height;
        std::string text;
        std::cin >> width >> height;
        std::cin.ignore();
        getline(std::cin, text);

        char chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ?";
        std::vector<std::vector<std::string> > letters;
        std::map<int, int> char2index;
        letters.resize(strlen(chars));
        std::cerr << text << std::endl;
        for (int l = 0; l < height; l++)
        {
                std::string line;
                getline(std::cin, line);
                //std::cerr << line << std::endl;

                for (size_t c = 0; c < letters.size(); c++)
                {
                    if (0 == l)
                    {
                        letters[c].resize(height);
                        char2index[chars[c]] = c;
                    }
                    letters[c][l] = line.substr(c*width, width);
                }
        }

        for (int l = 0; l < height; l++)
        {
            for (size_t c = 0; c < strlen(chars); c++)
            {
                std::cerr << letters[c][l];
            }
            std::cerr << std::endl;
        }

        for (int i = 0; i < height; i++)
        {
            for (size_t j = 0; j < text.length(); j++)
            {
                int c = toupper(text[j]);
                if (char2index.find(c) != char2index.end())
                {
                    std::cout << letters[char2index[c]][i];
                } else
                {
                    std::cout << letters[char2index['?']][i];
                }
            }
            std::cout << std::endl;
        }

        return 0;
}
