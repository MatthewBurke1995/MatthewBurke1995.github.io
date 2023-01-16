# The Friendship Paradox

On average your friends will have more friends than you. On average the football team you support will be one of the mosty popular football teams in the world. And the train or bus you took to work today was close to full capacity.

In graph theory there is a concept called "The Friendship Paradox" which stated plainly goes something like this "your friends have more friends than you". If we were to measure this, the recipe would look like:

## Procedure

1. Sample a random node (or ask a random person)
2. Count the number of edges (i.e. 'degree') for that node (how many friends can you count)
3. Calculate the degree for each neighbouring node (number of friends your friends have)
4. Take the average of the neighbouring nodes degrees 
5. Assert that the average degree of neighbouring nodes is higher than the degree of the randomly sampled node.

But it's also true that you or any other random node in the friendship graph could have more friends than the average node. The paradox occurs due to the difference in sampling methods.

Let's take the example of passengers catching a bus to see how this happens. Imagine there are only two busses in the world. One that takes 50 passengers and the other that takes 5 passengers.

If we ask each busdriver how many passengers they have we get an array of [50,5] for which the average is 27.5, a reasonable amount. But if we were to ask each passenger how many passengers are on the bus we get an array of [50, ..x48, 50, 5, 5, 5, 5, 5] with an average of:

\[
    mean(degree) = (50 * 50 + 5 * 5)/(50+5) ~= 45.9...
\] 

We have two 'averages' for the same metric with vastly different results depending on if we sample each node or each edge (or which type of node in the case of a bipartite graph). Using $k$ to represent the degrees of a node we can express the two alternatives as:

## Per node average

$$
    \sum_{i=0}^n \frac{k_i}{n} = <k>
$$


## Per degree average

$$
    \frac{<k^2>}{<k>}
$$

## What should you measure?

Which metric is more useful depends on the circumstances. If you are a busdriver then you will be assigned randomly to take on a bus route in which case the best estimate for the number of passengers at any one time is $ <k> $ but if you are a passenger then you are more likely to catch the bus during peek times for the same reason as everyone else, in which case the per degree average is a better estimate of how busy the bus will be. 

The same metaphor can works teachers and students in classrooms. And when we don't have a bipartite graph we end up with the friendship paradox.
