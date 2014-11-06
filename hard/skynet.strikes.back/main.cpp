/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-06
 */
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <list>
#include <set>
#include <map>

using namespace std;

class CGraph
{
    typedef std::set<int> incidence_t;
    typedef std::map<int, incidence_t> adjacency_t;
    typedef std::vector<int> weights_t;
    typedef std::set<int> exits_t;

    int m_nodes;
    adjacency_t m_adjacency;
    weights_t m_weights;
    exits_t m_exits;

    public:
        CGraph(int nodes): m_nodes(nodes), m_weights(nodes, 0)
        {
        }

        void add_edge(int i, int j)
        {
            m_adjacency[i].insert(j);
            m_adjacency[j].insert(i);
        }

        void remove_edge(int i, int j)
        {
            m_adjacency[i].erase(j);
            m_adjacency[j].erase(i);
            if (m_exits.end() != m_exits.find(i))
            {
                m_weights[j]--;
            }
            if (m_exits.end() != m_exits.find(j))
            {
                m_weights[i]--;
            }
        }

        void add_exit(int n)
        {
            m_exits.insert(n);
            adjacency_t::iterator j = m_adjacency.find(n);
            if (j != m_adjacency.end())
            {
                incidence_t& s = j->second;
                for (incidence_t::iterator k = s.begin(); k != s.end(); k++)
                {
                    m_weights[*k]++;
                }
            }
        }

        typedef std::list<int> path_t;
        path_t find_shortest_path(int from, int to) const
        {
            path_t result;
            std::vector<int> distance(m_nodes, 100500);
            std::set<int> visited;
            std::list<int> to_visit;
            for (exits_t::const_iterator e = m_exits.begin(); e != m_exits.end(); e++)
            {
                //std::cerr << "excl " << *e << std::endl;
                visited.insert(*e);
            }

            distance[from] = 0;
            to_visit.push_back(from);

            while (!to_visit.empty())
            {
                int v = to_visit.front();
                to_visit.pop_front();
                visited.insert(v);
                adjacency_t::const_iterator node = m_adjacency.find(v);
                for (incidence_t::const_iterator i = node->second.begin(); i != node->second.end(); i++)
                {
                    if (visited.end() == visited.find(*i))
                    {
                        to_visit.push_back(*i);
                    }
                    if (distance[*i] > distance[v] + 1 && m_exits.end() == m_exits.find(*i))
                    {
                        distance[*i] = 1 + distance[v];
                    }
                }
            }

            for (size_t i = 0; i < distance.size(); i++)
            {
                //std::cerr << "distance to node #" << i << " is " << distance[i] << std::endl;
            }

            //Build result
            if (100500 == distance[to])
            {
                // No path found
                return result;
            }

            int n = to;
            result.push_front(n);
            while (n != from)
            {
                adjacency_t::const_iterator node = m_adjacency.find(n);
                for (incidence_t::const_iterator i = node->second.begin(); i != node->second.end(); i++)
                {
                    if (distance[*i] < distance[n])
                    {
                        result.push_front(*i);
                        n = *i;
                        break;
                    }
                }
            }

            return result;
        }

        typedef std::pair<int, path_t> way_t;
        class cmp
        {
            public:
                cmp() {}
                bool operator()(const way_t& a, const way_t& b) const
                {
                    /*
                    bool result = false;
                    if (a.second.size() < 3 && b.second.size() >= 3)
                    {
                        result = true;
                    } else if (a.second.size() >= 3 && b.second.size() >= 3)
                    {
                        result = a.first > b.first
                            || (a.first == b.first && a.second.size() < b.second.size());
                    }
                    return result;
                    */
                    return a.second.size() - a.first < b.second.size() - b.first
                        || (a.second.size() - a.first == b.second.size() - b.first && a.second.size() < b.second.size());
                }
        };
        
        void dump_weights() const
        {
            for (size_t i = 0; i < m_weights.size(); i++)
            {
                std::cerr << "wn #" << i << " is " << m_weights[i] << std::endl;
            }
        }
        
        void dump_way(const way_t& w) const
        {
            std::cerr << "w is " << w.first << "(" << w.second.size() << ", " << w.second.size() - w.first <<  "): ";
            bool first = true;
            for (path_t::const_iterator i = w.second.begin(); i != w.second.end(); i++)
            {
                std::cerr << (first ? "" : " -> ") << *i;
                first = false;
            }
            std::cerr << std::endl;
        }

        typedef std::set<way_t, cmp> ways_t;
        ways_t find_all_ways(int from, int to) const
        {
            ways_t result;
            adjacency_t::const_iterator i = m_adjacency.find(to);
            if (m_adjacency.end() == i)
            {
                return result;
            }

            for (incidence_t::const_iterator j = i->second.begin(); j != i->second.end(); j++)
            {
                if (0 == m_weights[*j])
                {
                    std::cerr << "Broken logic" << std::endl;
                }

                path_t path = find_shortest_path(from, *j);
                if (!path.empty())
                {
                    path.push_back(to);
                    int weight = 0;
                    for (path_t::const_iterator p = path.begin(); p != path.end(); p++)
                    {
                        weight += m_weights[*p];
                    }
                    way_t w(weight, path);
                    std::cerr << "fw: ";
                    dump_way(w);
                    result.insert(w);
                }
            }

            return result;
        }

        path_t find_best_path(int from) const
        {
            ways_t result;
            for (exits_t::const_iterator e = m_exits.begin(); e != m_exits.end(); e++)
            {
                ways_t ways = find_all_ways(from, *e);
                for (ways_t::const_iterator i = ways.begin(); i != ways.end(); i++)
                {
                    result.insert(*i);
                }
            }

            if (result.empty())
            {
                std::cerr << "Invalid situation" << std::endl;
            }

            return result.begin()->second;
        }
};

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int N; // the total number of nodes in the level, including the gateways
    int L; // the number of links
    int E; // the number of exit gateways
    cin >> N >> L >> E; cin.ignore();
    std::cerr << N << " " << L << " " << E << std::endl;
    CGraph net(N);
    for (int i = 0; i < L; i++)
    {
        int N1; // N1 and N2 defines a link between these nodes
        int N2;
        cin >> N1 >> N2; cin.ignore();
        std::cerr << N1 << " " << N2 << std::endl;
        net.add_edge(N1, N2);
    }

    for (int i = 0; i < E; i++)
    {
        int g;
        cin >> g;
        cin.ignore();
        std::cerr << g << std::endl;
        net.add_exit(g);
    }

    // game loop
    while (1)
    {
        int SI; // The index of the node on which the Skynet agent is positioned this turn
        cin >> SI; cin.ignore();
        std::cerr << "Virus at node #" << SI << std::endl;
        net.dump_weights();

        CGraph::path_t result;
        for (int i = 0; i < E; i++)
        {
            //std::cerr << "Find path to #" << gates[i] << " gate..." << std::endl;
            CGraph::path_t path = net.find_best_path(SI);
            bool first = true;
            for (CGraph::path_t::const_iterator i = path.begin(); i != path.end(); i++)
            {
                std::cerr << (first ? "" : " -> ") << *i;
                first = false;
            }
            std::cerr << endl;

            if (result.empty()
                || (!path.empty() && result.size() > path.size()))
            {
                result = path;
            }
        }
        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;

        if (result.empty())
        {
            std::cerr << "result is empty" << std::endl;
            return 1;
        }

        int from = result.back();
        result.pop_back();
        int to = result.back();
        net.remove_edge(from, to);
        net.dump_weights();
        cout << from << " " << to << endl; // Example: 0 1 are the indices of the nodes you wish to sever the link between
    }
}
