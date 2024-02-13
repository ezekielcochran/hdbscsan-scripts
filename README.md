# Evaluating the uniqueness of minimum spanning trees for the context of HDBSCAN
The main.py script feeds a given data set to HDBSCAN twice: once in the given order, and once shuffled. It then reports whether the resulting minimum spanning trees are identical, and attempts to graph them side by side.

We have established that minimum spanning trees are not unique, and that the HDBSCAN algorithm to generate them gives different ones based on the order of the data.

But not just for weird, taylor-made exceptions, it seems to happen often in real-world data as well.

### Todo
+ Add more data sets as examples
+ Classify when exactly we get multiple MSTs
  + NEC*k*Sc metric spaces
    + In terms of the relation between the kissing number and the cluster size *k*
    + Good bound in small dimension, poor bound in higher dimensions
+ Potentially talk about *probability* of getting different MSTs given random data order
