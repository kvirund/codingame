/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
 */
// Read inputs from stdin. Write outputs to stdout.

#include <iostream>
#include <string>
#include <map>
#include <algorithm>

using namespace std;

int main()
{
	int types, files;
	cin >> types; cin.ignore();
	cin >> files; cin.ignore();
	
	std::cerr << types << ", " << files << std::endl;
	
	std::map<std::string, std::string> mime_types;
	for (int i = 0; i < types; i++)
	{
	    std::string type;
	    std::string mime;
		std::cin >> type >> mime;
		std::cin.ignore();
		
		std::cerr << "type: " << type << ", mime: " << mime << std::endl;
		std::transform(type.begin(), type.end(), type.begin(), ::tolower);
		mime_types[type] = mime;
	}
	
	for (int i = 0; i < files; i++)
	{
	    std::string filename;
	    std::cin >> filename;
	    std::cin.ignore();
	    std::transform(filename.begin(), filename.end(), filename.begin(), ::tolower);
	    size_t pos = filename.rfind('.');
	    std::cerr << "file #" << i << ". " << filename << "; rpos = " << pos << ", npos = " << std::string::npos << std::endl;
	    
	    if (std::string::npos != pos)
	    {
	        std::string ext = filename.substr(pos + 1);
	        //std::cerr << pos << ", " << ext <<  std::endl;
	        std::map<std::string, std::string>::const_iterator i = mime_types.find(ext);
	        if (mime_types.end() == i)
	        {
	            std::cout << "UNKNOWN" << std::endl;
	        } else
	        {
	            std::cout << i->second << std::endl;
	        }
	    } else
	    {
	        std::cout << "UNKNOWN" << std::endl;
	    }
	}
	
	return 0;
}
