So I like going to [zlbb.faendir.com](https://zlbb.faendir.com/) and looking at the Pareto Frontier solutions. A solution is part of the Pareto Frontier when there are no other solutions that are "strictly" better than it. So for example the solution ( 140g / 15c / 13a ) is strictly better than ( 140g / 16c / 15a ) because it is faster and smaller, but is not strictly better than ( 90g / 21c / 13a ) because it is more expensive even though it is faster.

The problem is that it gets difficult to compare different Pareto Frontier solutions in any meaningful way because that are so vastly different. But reading up on the [Pareto Frontier](https://en.wikipedia.org/wiki/Pareto_front) it keeps talking about assigning weights to each metric, and if I understand correctly for each solution in the front there is a set of weights that will make it the best.

So for example if you value the speed of a solution 70% the size 20% and the cost 10% there is a single pareto front solution that will minimize those weights.

Something clicked in my brain when I saw that, and it made me think of [Ternary Plots](https://en.wikipedia.org/wiki/Ternary_plot), which are specifically built for visualizing 3 percentages. And I realized that I could plot which solution is the best for every single possible set of weights.

So I got started putting together some scapy python code to see if this thing would actually work. Luckily [zlbb.faendir.com](https://zlbb.faendir.com) has a nice api for pulling all of the solutions that have been submitted, so huge shout out to them. And about 30 hours of work later (it was way more complicated than I could have expected) I got this site put together:

[https://benjameep.github.io/opus-magnum-ternary-plots](https://benjameep.github.io/opus-magnum-ternary-plots)

For now, the chart is lacking labels (we'll see if I ever come back and fix that). So you'll just have to imagine it has the following labels:

                              Fastest
                                /\
                               /  \
                        large /    \ expensive
                             /      \
                            /________\
                   Cheapest    slow     Smallest

  
Features:

* Clicking on an area will show the gif of the solution 
* Search bar for looking up a specific puzzle
* If you haven't searched for a puzzle a random one is shown (so you can just keep refreshing the page to see a whole bunch of random ones)

The algorithm that I developed to generate the polygons from taking point samples is quite complicated and bug prone, so let me know if you find any charts that have missing or overlapping polygons, and I'll see if I can figure out a way to fix it :)
