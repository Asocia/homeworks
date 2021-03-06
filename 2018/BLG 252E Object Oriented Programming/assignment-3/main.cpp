/* @Author
* Student Name: Şahin Akkaya
* Student ID : 150170098
* Date: 09.05.2019 */

#include <algorithm>
#include <functional>
#include "helper_functions.h"
#include "menu.h"
#include "order.h"
#include "stock.h"
using namespace std;

void serve_to_tables(Stock&, Menu&, Order&);

int main() {
    string file_names[] = {"stock", "menu", "order"};
    map<string, ifstream*> files;
    if (!open_files(file_names, 3, files))  // If cannot open any of the files
        return EXIT_FAILURE;

    Stock stock(*files["stock"]);
    Menu menu(*files["menu"]);
    Order order(*files["order"]);

    serve_to_tables(stock, menu, order);
    stock.write_to_file();

    close_files(file_names, 3, files);
    return EXIT_SUCCESS;
    // https://www.youtube.com/watch?v=Wmc8bQoL-J0
}

/*
 /brief process orders and print messages for them
 /param s a reference to Stock that keeps the current stock
 /param m a reference to Menu that keeps restaurant’s menu information
 /param o a reference to Order that keeps orders of the tables.
*/
void serve_to_tables(Stock& s, Menu& m, Order& o) {
    for (auto const& table : o.get_tables()) {
        string table_name = get<0>(table);
        vector<tuple<string, int>> orders = get<1>(table);
        double total_cost = 0, cost, tip, tax;

        cout << table_name << " ordered:" << endl;
        for (auto const& order : orders) {
            string order_name = get<0>(order);
            int number_of_orders = get<1>(order);
            vector<tuple<string, int>> requirements = m.get_menu()[order_name];

            auto requirement_satisfied = bind(&Stock::has_enough, &s, placeholders::_1, cref(number_of_orders));
            bool can_be_served = all_of(requirements.begin(), requirements.end(), requirement_satisfied);

            if (!can_be_served) {
                cout << "We don't have enough " << order_name << endl;
            }
            while (!can_be_served && number_of_orders > 0) {
                number_of_orders -= 1;
                can_be_served = all_of(requirements.begin(), requirements.end(), requirement_satisfied);
            }
            if (number_of_orders > 0) {
                cost = 0;
                for (auto const& req : requirements) {
                    string requirement_name = get<0>(req);
                    int required_amount = get<1>(req);
                    s.update(requirement_name, required_amount * number_of_orders);
                    cost += s.get_price(requirement_name, required_amount * number_of_orders);
                }
                cout << number_of_orders << " " << order_name << " cost: " << cost << endl;
                total_cost += cost;
            }
        }
        tip = total_cost * 0.15;
        tax = total_cost * 0.08;
        total_cost = total_cost + tip + tax;
        cout << "Tip is " << tip << endl;
        cout << "Total cost: " << total_cost << " TL" << endl;
        cout << "*********************" << endl;
    }
}
