# /usr/bin/python3.8
from typing import List, Tuple, Optional
from collections import deque


class Attack:
    """A class to represent an attack"""

    def __init__(self, name: str, cost: str,
                 accuracy: str, damage: str, first_usage: str) -> None:
        """
        :param name: name of the attack
        :param cost: the integer that will be decreased from attacker's pp
        :param accuracy: the probability that the attack will succeed (0-100)
        :param damage: the integer that will be decreased from defender's hp
                       if the attack is succeeded
        :param first_usage: the first round where the attack may be used
        """
        self.name = name
        self.cost = -int(cost)
        self.accuracy = int(accuracy) / 100
        self.inaccuracy = 1 - self.accuracy
        self.damage = int(damage)
        self.first_usage = int(first_usage)

    def __repr__(self):
        return f"{self.name}, {self.cost}, {self.accuracy}, " \
               f"{self.damage}, {self.first_usage}"


class Pokemon:
    """A class to represent pokemons"""
    ATTACKS = {"pikachu": [], "blastoise": []}

    def __init__(self, name: str, health_points: int, power_points: int) -> None:
        """
        :param name: name of the pokemon, either 'pikachu' or 'blastoise'
        :param health_points: the integer that holds the initial HP of pokemon
        :param power_points: the integer that holds the initial PP of pokemon
        """
        self.health_points = health_points
        self.power_points = power_points
        self.is_pikachu = name == "pikachu"
        assert name in ("pikachu", "blastoise"), \
            "name of the pokemon should be 'pikachu' or 'blastoise'"
        if not self.ATTACKS[name]:
            self.ATTACKS[name].extend(self.__read_attacks_file(name))

    @staticmethod
    def __read_attacks_file(name):
        """
        Reads attacks file for pokemon specified by name and returns
        list of attacks that the pokemon can do
        """
        with open(name + ".txt") as f:
            f.readline()
            return [Attack(*line.split(",")) for line in f.readlines()]

    @property
    def __attacks(self):
        """Returns list of all attacks that the pokemon can do"""
        name = "pikachu" if self.is_pikachu else "blastoise"
        return self.ATTACKS[name]

    def get_attacks(self, level: int) -> List[Attack]:
        """
        Takes an integer, level, and returns possible attacks for
        that level
        """
        return [attack for attack in self.__attacks
                if attack.first_usage <= level and attack.cost <= self.power_points]

    def copy(self) -> 'Pokemon':
        d = self.__dict__.copy()
        d["name"] = "pikachu" if self.is_pikachu else "blastoise"
        d.pop("is_pikachu")
        return Pokemon(**d)

    def attack(self, opponent: 'Pokemon', attack: Attack, effective: bool) -> None:
        """
        Attacks to the opponent with specified attack and do damage
        if effective is True
        """
        self.power_points -= attack.cost
        if effective:
            opponent.health_points -= attack.damage
            if opponent.health_points < 0:
                opponent.health_points = 0

    def __repr__(self):
        name = "pikachu" if self.is_pikachu else "blastoise"
        return f"Pokemon('{name}', {self.health_points}, {self.power_points})"

    def __str__(self):
        i = "P" if self.is_pikachu else "B"
        return f"{i}_HP:{self.health_points} {i}_PP:{self.power_points}"


class Node:
    """A class to represent a state in the game"""
    END_FLAG = []

    def __init__(self, pokemons: Tuple[Pokemon, Pokemon],
                 probability: float, level: int, parent: 'Node' = None,
                 attack_name: str = None, is_effective: bool = None,
                 is_leaf: Optional[bool] = True) -> None:
        """
        :param pokemons: a pair of Pokemon instances where the next attacker comes
                        first
        :param probability: the probability of encountering this state in the
                            game
        :param level: an integer that shows the level of this state
        :param parent: parent of the node
        :param attack_name: name of the attack used to reach this state
        :param is_effective: effectiveness of the attack
        :param is_leaf: a boolean that tells if this state is end of game
        """
        self.attacker, self.defender = pokemons
        self.probability = probability
        self.level = level
        self.parent = parent
        self.attack_name = attack_name
        self.is_effective = is_effective
        self.is_leaf = is_leaf
        self.children = []

    def create_levels_until(self, max_level: Optional[int] = 999,
                            winner: Optional[str] = "",
                            verbose: Optional[bool] = True) -> None:
        """
        Creates levels until number of levels reaches max_level OR
        winner wins the game
        """
        leaves = deque()
        node = self
        while not Node.END_FLAG:
            if node.level == max_level:
                break
            children = []
            winner_is_pikachu = winner == "pikachu"
            if node.attacker.health_points > 0:
                possible_attacks = node.attacker.get_attacks(node.level)
                num_attacks = len(possible_attacks)
                for attack in possible_attacks:
                    effective = True
                    attacker, defender, n = self.__spawn_node(node, attack,
                                                              effective,
                                                              num_attacks, max_level,
                                                              verbose)
                    if self.__end_of_game(attacker, defender, winner,
                                          winner_is_pikachu):
                        Node.END_FLAG.append(True)
                    children.append(n)

                    if attack.accuracy != 1:
                        effective = False
                        attacker, defender, n = self.__spawn_node(node, attack,
                                                                  effective,
                                                                  num_attacks,
                                                                  max_level,
                                                                  verbose)
                        children.append(n)

            if len(children) > 0:
                node.is_leaf = False
                node.children.extend(children)
                leaves.extend(children)
            node = leaves.popleft()

        if node == self:
            print(node)

    @staticmethod
    def __end_of_game(attacker, defender, winner, winner_is_pikachu):
        if defender.health_points == 0 and attacker.is_pikachu == winner_is_pikachu:
            if winner in ("pikachu", "blastoise"):
                return True
        return False

    @staticmethod
    def __spawn_node(node, attack, effective, num_attacks, max_level, verbose):
        attacker, defender = node.attacker.copy(), node.defender.copy()
        attacker.attack(defender, attack, effective=effective)
        mul = attack.accuracy if effective else attack.inaccuracy
        probability = node.probability / num_attacks * mul
        n = Node((defender, attacker), probability, node.level + 1, node,
                 attack.name, effective)
        if verbose and n.level == max_level:
            print(n)
        return attacker, defender, n

    @staticmethod
    def breadth_first_traversal(root_node: 'Node',
                                verbose: Optional[bool] = False) -> int:
        """
        Performs a level order traversal on tree that has root 'root_node' and
        returns number of nodes
        """
        if root_node is None:
            return 0
        node_count = 0
        queue = deque((root_node,))

        while len(queue) > 0:
            node_count += 1
            node = queue.popleft()
            if verbose:
                print(node)
            queue.extend(node.children)

        return node_count

    @staticmethod
    def breadth_first_search(root_node: 'Node', winner: str):
        if root_node is None:
            return None
        queue = deque((root_node,))
        winner_is_pikachu = winner == "pikachu"
        while len(queue) > 0:
            node = queue.popleft()
            if Node.__end_of_game(node.defender, node.attacker, winner,
                                  winner_is_pikachu):
                return node
            queue.extend(node.children)

        return None

    @staticmethod
    def depth_first_traversal(root_node: 'Node',
                              verbose: Optional[bool] = False) -> int:
        """
        Performs pre order traversal on tree that has root 'root_node' and
        returns number of nodes
        """
        if root_node is None:
            return 0
        node_count = 0
        stack = [root_node]
        while len(stack) > 0:
            node_count += 1
            node = stack.pop()
            if verbose:
                print(node)
            stack.extend(reversed(node.children))
        return node_count

    def __str__(self):
        pikachu = self.attacker if self.attacker.is_pikachu else self.defender
        blastoise = self.defender if self.attacker.is_pikachu else self.attacker
        return " ".join(map(str, (pikachu, blastoise, f"PROB:{self.probability:.7f}")))


def main():
    import sys
    import time
    start = time.perf_counter()
    pikachu = Pokemon("pikachu", 200, 100)
    blastoise = Pokemon("blastoise", 200, 100)
    n = Node((pikachu, blastoise), 1.0, 0)
    verbose = sys.argv[-1] == "v"
    if sys.argv[1] == "part1":
        max_level = int(sys.argv[2])
        n.create_levels_until(max_level, verbose=verbose)
    elif sys.argv[1] == "part2":
        max_level = int(sys.argv[2])
        n.create_levels_until(max_level, verbose=False)
        if sys.argv[3] == "bfs":
            node_count = Node.breadth_first_traversal(n, verbose)
        elif sys.argv[3] == "dfs":
            node_count = Node.depth_first_traversal(n, verbose)
        else:
            raise Exception

        print(f"node count is: {node_count:,}")
    elif sys.argv[1] == "part3":
        n.create_levels_until(winner=sys.argv[2], verbose=False)
        node = Node.breadth_first_search(n, sys.argv[2])
        list_of_nodes = []
        while node.parent:
            list_of_nodes.append(node)
            node = node.parent

        while list_of_nodes:
            node = list_of_nodes.pop()
            if node.attacker.is_pikachu:
                prev_attacker = "Blastoise"
                pikachu_hp = node.attacker.health_points
                blastoise_hp = node.defender.health_points
            else:
                prev_attacker = "Pikachu"
                pikachu_hp = node.defender.health_points
                blastoise_hp = node.attacker.health_points

            attack_name = node.attack_name
            is_effective = "Effective" if node.is_effective else "Noneffective"
            print(f"{prev_attacker} used {attack_name}. {is_effective} "
                  f"(P:{pikachu_hp}, B:{blastoise_hp})")

        print(f"Level count: {node.level}")
        print(f"Probability: {node.probability}")

    total = time.perf_counter() - start
    print(f"Took {total:.2f} seconds to execute")


if __name__ == '__main__':
    main()
