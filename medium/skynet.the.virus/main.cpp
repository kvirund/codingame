/**
 * \author Anton Gorev aka Veei
 * \date 2014-11-05
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
    adjacency_t m_adjacency;
    int m_nodes;

    public:
        CGraph(int nodes): m_nodes(nodes)
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
        }

        typedef std::list<int> path_t;
        path_t find_shortest_path(int from, int to) const
        {
            path_t result;
            std::vector<int> distance(m_nodes, 100500);
            std::set<int> visited;
            std::list<int> to_visit;

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
                    if (distance[*i] > distance[v] + 1)
                    {
                        distance[*i] = 1 + distance[v];
                    }
                }
            }

            for (size_t i = 0; i < distance.size(); i++)
            {
                std::cerr << "distance to node #" << i << " is " << distance[i] << std::endl;
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

    std::vector<int> gates(E);
    for (int i = 0; i < E; i++)
    {
        cin >> gates[i]; cin.ignore();
        std::cerr << gates[i] << std::endl;
    }

    // game loop
    while (1)
    {
        int SI; // The index of the node on which the Skynet agent is positioned this turn
        cin >> SI; cin.ignore();

        CGraph::path_t result;
        for (int i = 0; i < E; i++)
        {
            std::cerr << "Find path to #" << gates[i] << " gate..." << std::endl;
            CGraph::path_t path = net.find_shortest_path(SI, gates[i]);
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
            //We have won
            return 1;
        }
        
        int from = result.back();
        result.pop_back();
        int to = result.back();
        net.remove_edge(from, to);
        cout << from << " " << to << endl; // Example: 0 1 are the indices of the nodes you wish to sever the link between
    }
}
