astar(Node, Path, Cost) :- kb(KB),
			   astar2([[Node, [], 0]], Path, Cost, KB).

astar2([[Node, Path, Cost]|_], [Node, Path], Cost, _) :- goal(Node).
astar2([[Node, P, C]| Rest], Path, Cost, KB) :-
	findall([X, [Node|P], Sum], (arc(Node, X, Y, KB), Sum is Y+C), Children),
	append(Children, Frontier, NewFrontier),
	sortfrontier(Temp, [[N1, P1, C1]| T1]),
	astar2([[N1, P1, C1]| T1], Path, Cost, KB).

sortfrontier([Head|Tail], Result) :- sort(Head, [], Tail, Result).

sort(Head, S, [], [Head|S]).
sort(C, S, [Head|Tail], Result) :-
	lessthan(C, Head), !,
	sort(C, [Head|S], Tail, Result);
	sort(Head, [C|S], Tail, Result).

lessthan([Node1, _, Cost1| _], [Node2, _, Cost2| _]) :-
	heuristic(Node1, Hvalue1),
	heuristic(Node2, Hvalue2),
	F1 is Cost1+Hvalue1,
	F2 is Cost2+Hvalue2,
	F1 =< F2.

heurisitc(Node, H) :- length(Node, H).

goal([]).



arc([H|T], Node, Cost, KB) :-
	member([H|B], KB),
	append(B, T, Node),
	length(B, L),
	Cost is L+1.
