/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
// Read inputs from stdin. Write outputs to stdout.

#include <iostream>
#include <string>
#include <vector>

using namespace std;

int main()
{
	std::string input;
	getline(cin, input);

    std::cerr << input << std::endl;
    
    std::string result;
    int last_char = -1;
    for (size_t i = 0; i < input.size(); i++)
    {
        for (size_t j = 0; j < 7; j++)
        {
            int bit = input[i] & (0x01 << (6 - j)) ? 1 : 0;
            if (-1 == last_char
                || bit != last_char)
            {
                result += (-1 == last_char ? "" : " ");
                result += (1 == bit ? "0 " : "00 ");
                last_char = bit;
            }
            result += '0';
            std::cerr << (1 == bit ? '1' : '0');
        }
        std::cerr << std::endl;
    }
    std::cout << result << std::endl;
    
	return 0;
}
