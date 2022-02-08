from util import Expr, expr, conjuncts
import copy
import json


class Goal:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.state = list()
        self.previousGoals = list()
        self.previousActions = list(list())

    def expandGoals(self, actions, previousState):
        """find previous actions to achieve the current goal and the 
        preconditions of those actions that corresponds to the subgoals of the goal"""

        self.previousActions = self.findPreviousActions(actions)
        aux = len(self.previousActions)

        for i in range(0, aux):
            for pre in self.previousActions[i].preconditions:
                subgoal = Goal(pre)
                subgoal.parent = self
                self.previousGoals.append(subgoal)

            # g' = (g - effects(a)) + preconds(a)
            self.state.append((previousState.difference(
                set(self.previousActions[i].effect))).union(set(self.previousActions[i].preconditions)))

    def findPreviousActions(self, actions):
        """return a list of possible actions to achieve the goal"""

        result = list()
        for action in actions:
            for eff in action.effect:
                if eff == self.name:
                    result.append(action)
        return result


class PlanningProblem:

    def __init__(self, initial, goals, actions):
        self.initial = self.convert(initial)
        self.goals = self.convert(goals)
        self.actions = actions

    def convert(self, clauses):
        """Converts strings into exprs"""
        if not isinstance(clauses, Expr):
            if len(clauses) > 0:
                clauses = expr(clauses)
            else:
                clauses = []
        try:
            clauses = conjuncts(clauses)
        except AttributeError:
            pass

        new_clauses = []
        for clause in clauses:
            if clause.op == '~':
                new_clauses.append(expr('Not' + str(clause.args[0])))
            else:
                new_clauses.append(clause)
        return new_clauses

    def backwardPlanning(self, start=True):
        """function that test every action if it has the effects of the current goal
        trying to find the action that is more likely the initial state"""

        state = set(copy.deepcopy(self.goals))
        tmp = list()

        if start:
            start = False
            for g in self.goals:
                tempG = Goal(g)
                tempG.expandGoals(self.actions, state)
                tmp.append(tempG)
                if tempG.state == self.initial:
                    print("Solution Found")
                    return

        """for each new subgoal find their subgoals
        while subgoals states is not the initial"""

        for tm in tmp:
            for substate in tm.state:
                for subgoal in substate:
                    if subgoal not in self.initial:
                        subgoal = Goal(subgoal)
                        subgoal.parent = tm
                        Goal.expandGoals(
                            subgoal, self.actions, substate)
                        tmp.append(subgoal)

                        """check if state is the initial"""
                        for s in subgoal.state:
                            if s == set(self.initial):
                                # get actions list
                                actionsList = list()

                                while subgoal != None:
                                    for e in self.actions:
                                        if subgoal.name in e.effect:
                                            actionsList.append(e)
                                            subgoal = subgoal.parent
                                            break

                                for action in actionsList:
                                    print(action.name, action.args)
                                return True


class Action:

    def __init__(self, action, preconditions, effect):
        if isinstance(action, str):
            action = expr(action)
        self.name = action.op
        self.args = action.args
        self.preconditions = self.convert(preconditions)
        self.effect = self.convert(effect)

    def convert(self, clauses):
        """Converts strings into Exprs"""
        if isinstance(clauses, Expr):
            clauses = conjuncts(clauses)
            for i in range(len(clauses)):
                if clauses[i].op == '~':
                    clauses[i] = expr('Not' + str(clauses[i].args[0]))

        elif isinstance(clauses, str):
            clauses = clauses.replace('~', 'Not')
            if len(clauses) > 0:
                clauses = expr(clauses)

            try:
                clauses = conjuncts(clauses)
            except AttributeError:
                pass

        return clauses

    def negate_clause(clause):
        return Expr(clause.op.replace('Not', ''), *clause.args) if clause.op[:3] == 'Not' else Expr(
            'Not' + clause.op, *clause.args)


def main():

    # read from file the problem initial state and goals
    with open('IndustryProblemInfo.json', 'r') as fp:
        problemData = json.load(fp)

    initial = problemData[0]
    goals = problemData[1]

    # read from file the actions of the problem
    with open('industryActionsInfo.json', 'r') as fp:
        actionsData = json.load(fp)

    actionList = list()
    for act in actionsData:
        actionList.append(Action(act[0], act[1], act[2]))

    # initialize the problem and solve it
    pp = PlanningProblem(initial, goals, actionList)
    pp.backwardPlanning()


main()
