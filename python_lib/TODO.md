Things to do:

Now, part 1.5:

Make it possible to use params in expressions. It's simpler now, as reading
a param is the only valid use for the dollar sign.
After that, allow expressions in tons of different places where I do
QuotedOrVar. In particular, allow expressions in the "AS" part of a column
definition, which allows me to use things like "name(1)" there.
And, at this point, finish implementing committee_data/remove_zero_parties.cfg.
Also, fix the 1:2 hack in sejm_election_results/just_votes.cfg.

After defining this (which should be easy) remove all the exclamation marks
and the question marks and dollars from all over the place, simplify the
damn GetValueFromContext, and kill the ReferVariable.

Now, part 2:

Define a "columns touched" method on the expression. For range expressions,
it always contains curr(). For weirdo stuff it returns some weirdo thing.
The point is that if there's exactly one column referenced, then the AS
clause is optional - so, after consuming the expression, we check whether
there's exactly one column touched, and if so, make the AS part optional.

Now, part 3:

Defining ranges. Is broken. We should admit expressions in range defs, that
are evaluated just as headers are (so, in a context that allows me to use
name and value, and also curr_name if I'm in a range column def context).

I also think the square brackets should be either required or disallowed.
The question is basically: can I get away with not asking for them? And then
the idea would be:
a) try to read the colon. If it's there, it means the beg is empty. If not,
read the expression and colon.
b) try to read the expression. If it succeeds, then it's the end. If it
fails to parse, then we should've read nothing. If we read something, then
throw. If we read nothing (because the first token was not a valid
expression beginning), then we proceed with the range being "last".

Sometime:

* Improve exception handling
* Allow parameter evaluation in the context of expressions
* Allow non-ASCII input in the terminal
* Allow setting parameters as a terminal-level map.
* Implicit column naming. When a column name isn't specified, we should
  check if there's exactly one column being referenced by the expression,
  and if yes, use that column's name implicitly.
* Allow parameters in column names in transform.
* Allow expressions in column names in single-column definitions.
