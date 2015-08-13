/**
 * \author Anton Gorev aka Veei
 * \date 2015-08-09
 */
#include <assert.h>

#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <map>

using namespace std;

const int TAPE_LENGTH = 30;
const int LETTERS_COUNT = ('Z' - 'A' + 1) + 1;    // letters count plus ' '

class debug
{
    public:
        static void log(const std::string& message)
        {
            if (s_on)
            {
                std::cerr << message << std::endl;
            }
        }

    private:
        static bool s_on;
};

bool debug::s_on = false;

template <int MODULUS>
class CNumber
{
    public:
        typedef CNumber<MODULUS> type;
        CNumber(): m_number(0) {}
        CNumber(const int number): m_number((number % MODULUS + MODULUS) % MODULUS) {}

        type operator+(const type& right) const { return type(m_number + right.m_number); }
        type operator-(const type& right) const { return type(m_number - right.m_number); }
        bool operator<(const type& right) const { return m_number < right.m_number; }
        operator int() const { return m_number; }

        int shortest(const type& right) const
        {
            // 1, 20 mod 30
            // 20 - 1 = 19
            // 1 - 20 = -19 mod 30 = 11
            if (*this < right)
            {
                return shortest_helper(right);
            }
            return -right.shortest_helper(*this);
        }

    private:
        int shortest_helper(const type& right) const
        {
            type p = right - *this;
            type n = *this - right;
            if (p < n)
            {
                return int(p);
            }
            return -int(n);
        }

        int m_number;
};

class CTape
{
    public:
        CTape(const int tape_lentgh = TAPE_LENGTH): m_tape(tape_lentgh)
        {
            m_l2t[' '] = 0;
            for (char i = 'A'; i <= 'Z'; ++i)
            {
                m_l2t[i] = i - 'A' + 1;
            }
            for (l2t_t::const_iterator i = m_l2t.begin(); i != m_l2t.end(); ++i)
            {
                std::stringstream ss;
                ss << i->first << " -> " << i->second;
                debug::log(ss.str());
            }
        }

        std::string optimize(const std::string& algorithm)
        {
            // TODO: Implement me
            return algorithm;
        }

        std::string produce(const std::string& phrase)
        {
            std::string result;
            for (std::string::size_type i = 0; i < phrase.size(); ++i)
            {
                result += produce_letter(phrase[i]);
            }
            result = optimize(result);
            return result;
        }

    private:
        typedef std::map<char, int> l2t_t;
        typedef std::vector<CNumber<LETTERS_COUNT> > tape_t;

        static std::string repeat(char what, int count)
        {
            std::string result;
            while (count--)
            {
                result += what;
            }
            return result;
        }

        static std::string get_algorithm(int move, int change)
        {
            std::stringstream r;
            r << "getting algorithm with " << move << " movings and " << change << " changes";
            debug::log(r.str());
            char dir = 0 < move ? '>' : '<';
            char cdir = 0 < change ? '+' : '-';
            return repeat(dir, std::abs(move)) + repeat(cdir, std::abs(change)) + '.';
        }

        std::string produce_letter(const char letter)
        {
            debug::log(std::string("producing letter ") + letter);
            std::string result;
            int min_pos = -1;
            int min_dist = TAPE_LENGTH + LETTERS_COUNT;  // Above in any way
            int min_move, min_change;
            for (tape_t::size_type i = 0; i < m_tape.size(); ++i)
            {
                int dist_move = m_pos.shortest(i);
                int dist_change = m_tape[i].shortest(m_l2t[letter]);
                int dist_res = std::abs(dist_move) + std::abs(dist_change);
                if (min_dist > dist_res)
                {
                    min_dist = dist_res;
                    min_move = dist_move;
                    min_change = dist_change;
                    min_pos = i;
                }
            }

            if (-1 == min_pos)
            {
                assert("broken logic");
            }

            result = get_algorithm(min_move, min_change);
            m_tape[min_pos] = m_l2t[letter];    // change tape
            m_pos = min_pos;                    // move pointer
            debug::log("produced result: " + result);
            return result;
        }

        tape_t m_tape;
        CNumber<TAPE_LENGTH> m_pos;
        l2t_t m_l2t;
};

int main()
{
    string magicPhrase;
    getline(cin, magicPhrase);

    CTape tape;

    cout << tape.produce(magicPhrase) << endl;

    return 0;
}
