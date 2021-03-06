//
// Created by sahin on 22/04/2020.
//

#ifndef ASSIGNMENT_2_HELPER_FUNCTIONS_H
#define ASSIGNMENT_2_HELPER_FUNCTIONS_H

#include <vector>
using namespace std;
typedef vector<pair<int, int>> Solution;
int **allocate_matrix(int node_count);

void print_matrix(int **matrix, int length);

int min_distance(const int *dist, const bool *sptSet, int node_count);


int print_solution(Solution&);
int get_intersection_node(Solution&, Solution&);
Solution get_shortest_path(int **graph, int src, int dst, int num_of_nodes, int starting_time = 0);
Solution select_shortest_path(int **graph, int src, int dst, int num_of_nodes, int starting_time, int intersection_node, Solution&);
Solution get_node_times(const int *parent, int *dist, int src, int j);
int get_duration(Solution &s);


#endif //ASSIGNMENT_2_HELPER_FUNCTIONS_H
