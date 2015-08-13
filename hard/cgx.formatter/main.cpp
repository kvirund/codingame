/**
 * \author Anton Gorev aka Veei
 * \date 2015-08-09
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <list>

#include <strings.h>

void indent(int l)
{
    for (int i = 0; i < l; i++)
    {
        std::cout << "    ";
    }
}

enum EToken
{
    UNKNOWN,
    LEFT_BRACE,
    RIGHT_BRACE,
    BOOLEAN,
    NUMBER,
    STRING,
    SEPARATOR,
    EQUAL
};

struct SToken
{
    EToken type;
    size_t start;
    size_t length;
    
    SToken(): type(UNKNOWN), start(-1), length(-1) {}
    SToken(EToken t, size_t s, size_t l): type(t), start(s), length(l) {}
};

void dump_token(const SToken& t)
{
    switch (t.type)
    {
        case LEFT_BRACE:
            std::cerr << "LEFT_BRACE: " << t.start << ", " << t.length << std::endl;
            break;
            
        case RIGHT_BRACE:
            std::cerr << "RIGHT_BRACE: " << t.start << ", " << t.length << std::endl;
            break;
            
        case BOOLEAN:
            std::cerr << "BOOLEAN: " << t.start << ", " << t.length << std::endl;
            break;
            
        case NUMBER:
            std::cerr << "NUMBER: " << t.start << ", " << t.length << std::endl;
            break;
            
        case STRING:
            std::cerr << "STRING: " << t.start << ", " << t.length << std::endl;
            break;
            
        case SEPARATOR:
            std::cerr << "SEPARATOR: " << t.start << ", " << t.length << std::endl;
            break;
            
        case EQUAL:
            std::cerr << "EQUAL: " << t.start << ", " << t.length << std::endl;
            break;
            
        default:
            std::cerr << "Unexpected value of token type" << std::endl;
    }
}

void handle_token(const std::string& v, size_t s, size_t l, std::list<SToken>& tokens)
{
    if (0 == l)
    {
        return;
    }
    
    std::string t = v.substr(s, l);
    if (0 == strcasecmp("true", t.c_str())
        || 0 == strcasecmp("false", t.c_str()))
    {
        tokens.push_back(SToken(BOOLEAN, s, l));
    }
    else if ('\'' == t[0])
    {
        tokens.push_back(SToken(STRING, s, l));
    }
    else
    {
        tokens.push_back(SToken(NUMBER, s, l));
    }
}

int main()
{
    int N;
    std::cin >> N;
    std::cin.ignore();
    
    std::string value;
    for (int i = 0; i < N; i++)
    {
        std::string CGXLine;
        std::getline(std::cin, CGXLine);
        value += CGXLine;
    }
    
    bool inside = false;
    size_t j = 0;
    size_t l = value.length();
    std::list<SToken> tokens;
    size_t start = 0;
    size_t length = 0;
    for (size_t i = 0; i < l; i++)
    {
        switch (value[i])
        {
            case ' ':
            case '\t':
                if (inside)
                {
                    length++;
                    continue;
                }
                else
                {
                    if (length > 0)
                    {
                        handle_token(value, start, length, tokens);
                        length = 0;
                    }
                    start = i + 1;
                }
                break;
                
            case '(':
                if (!inside)
                {
                    handle_token(value, start, length, tokens);
                    
                    length = 0;
                    start = i + 1;
                    tokens.push_back(SToken(LEFT_BRACE, i, 1));
                }
                else
                {
                    length++;
                }
                break;
                
            case ')':
                if (!inside)
                {
                    handle_token(value, start, length, tokens);
                    
                    length = 0;
                    start = i + 1;
                    tokens.push_back(SToken(RIGHT_BRACE, i, 1));
                }
                else
                {
                    length++;
                }
                break;

            case ';':
                if (!inside)
                {
                    handle_token(value, start, length, tokens);
                    
                    length = 0;
                    start = i + 1;
                    tokens.push_back(SToken(SEPARATOR, i, 1));
                }
                break;

            case '=':
                if (!inside)
                {
                    handle_token(value, start, length, tokens);
                    
                    length = 0;
                    start = i + 1;
                    tokens.push_back(SToken(EQUAL, i, 1));
                }
                else
                {
                    length++;
                }
                break;

            case '\'':
                inside = !inside;
                length++;
                break;

            default:
                length++;
                break;
        }
    }
    handle_token(value, start, length, tokens);
    std::vector<SToken> atokens(tokens.size());
    j = 0;
    for (std::list<SToken>::const_iterator i = tokens.begin(); i != tokens.end(); i++)
    {
        dump_token(*i);
        atokens[j++] = *i;
    }
    std::cerr << std::endl;
    
    int level = 0;
    for (size_t i = 0; i < atokens.size(); i++)
    {
        switch (atokens[i].type)
        {
            case LEFT_BRACE:
                if (0 < i)
                {
                    std::cout << '\n';
                }
                indent(level++);
                break;
                
            case RIGHT_BRACE:
                if (0 < i)
                {
                    std::cout << '\n';
                }
                indent(--level);
                break;
                
            case BOOLEAN:
                if (0 < i && EQUAL != atokens[i - 1].type)
                {
                    std::cout << '\n';
                    indent(level);
                }
                break;
                
            case NUMBER:
                if (0 < i && EQUAL != atokens[i - 1].type)
                {
                    std::cout << '\n';
                    indent(level);
                }
                break;
                
            case STRING:
                if (0 < i && EQUAL != atokens[i - 1].type)
                {
                    std::cout << '\n';
                    indent(level);
                }
                break;
                
            case SEPARATOR:
                //std::cerr << "SEPARATOR" << std::endl;
                break;
                
            case EQUAL:
                //std::cerr << "EQUAL" << std::endl;
                break;
                
            default:
                std::cerr << "Unexpected value of token type" << std::endl;
        }
        std::cout << value.substr(atokens[i].start, atokens[i].length);
    }
}
