# Table of Contents

1. [Main Idea of the Algorithm] (README.md#Main-Idea-of-the-Algorithm)
2. [Details of Implementation] (README.md#details-of-implementation)
3. [Future Works] (README.md#Future-Works)

##Main Idea of the Algorithm

[Back to Table of Contents] (README.md#table-of-contents)

- Build undirected graph (neighbor list stored in a dictionary), for each vertex, its neighbor list is a set (ignoring duplicates). Undirected means for every transaction, we add two edges into graph

- Based on the first order connection graph above, build a second order one (merge neighbor lists of all neighbors of a vertex)

- In final checking, for each transaction, if one of the user not in the vertex list in degree 1 graph, it is sure to be unverified

- If a transaction as an edge can be found in degree 1 graph, all 3 outputs (3 features) will be trusted

- If a transaction as an edge can be found in degree 2 graph, output2 and output3 are trusted.

- For a transaction src -> dst, obtain degree 1, 2 neighbor lists of src, and degree 2 neighbor list of dst. Looping through the neighbor list of dst, if any user exists in the neighbor lists of src above, return trusted. After the looping, if not return, then return unverified.  

**Explain: The first 5 steps are trivial. I focus on the explanation of the last step here. To check if user2 is within degree 4 connection of user1, we can consider 2 cases (assume degree 1 and degree 2 have been checked):  
1) Degree 3: in this case, there must be one user3, who is degree 1 connection of user1, and also degree 2 connection of user2. We just need to get neighbor list of user1 in degree1 graph, neighbor list of user2 in degree2 graph, and see if these two lists have intersection.  
2) Degree 4: in this case, there must be one user3, who is degree 2 connection of user1 as well as user2. We just need to get neighbor lists of user1 and user2 in degree2 graph, and see if these two lists have intersection.  

- Scalability: If we cache only first order connection, the batch building step takes O(n*k) in average, assuming n users and avergely k connections per
user. And in checking step, feature1 takes O(1), feature2 takes $O(k^2)$, feature3 takes $O(k^4)$ for each user. If we cache second order connection
 also, feature1 takes $O(1)$, feature2 takes $O(1)$, feature3 takes $O(k^2)$. But if we need to update the cached graphs with new transaction, only cache 
first order takes $O(k)$, cache also second order takes $O(k^2)$. We can conclude, by caching second order connection, real time alerting has lower 
latency, but graph updating will take longer. In real application we actually care more about the latency of alerting. For transaction updating, we 
can tolerate some delay. And the speed gain from caching second order in alerting is much larger than the speed loss in transaction updating. This is 
a big trade-off and considering real application, I decided to use second order connection caching.  

##Details of implementation

[Back to Table of Contents] (README.md#table-of-contents)
- Dependencies: python 2.7, anaconda 1.18.2 (2015), (dependencies not included in the submitted version: spark 1.6.0 on hadoop 2.6)

- Usage: sh run.sh (the code calls unit test first, then cleans the output from unit test, and at last call the main run for big inputs)

- I use python for the coding challenge. The main source code is src/main/antifraud.py. because it is a relatively small code, we organize the codes with a main function wrapping all other utilities on the same file. 

- Main function first call read\_input to read batch\_input and clean the information (only second and third columns are useful for the analysis). The input batch data is stored in a list of tuples (id1, id2). build\_degree1\_graph then reads the list in and output a map of neighbor lists (python dictionary) representing the first order connection relationship. build\_degree2\_graph then reads this map in and output the second order connection map. After that, main function reads the stream input and also stores it in a list of tuples. For each tuple, we first check if any id is not presented in first order map keys. Then check degree1 graph and degree2 graph sequentially. If none of above can decide the relation of degree 4, we then apply the method described in step 6 of algorithm. 

- Unit tests: three unit tests are implemented in /src/test/antifraud_test.py. A simple version of input is created in paymo_input which only contains 10 record for batch and 4 records for streaming. The shell file run.sh calls unit test first and we can see all the tests can pass. 

- Multithread: for disctionary writes, I tested on multithreading. However, the speed is not improved. The reason might be the data set is still not very big and each thread is too small. The submitted version is without multithread which performs better on test set. 

- Memory: because I cache the second order connections, the memory usage is big which is about 4.8 GB. Consider this is acceptable for most present-day machines, I keep this version. If memory is really a concern, it is possible to only cache first order connections which will be slower because feature2 and feature3 require the calculation of second order connections. 

- Time: in the submit version, time for run through all 3 feature is 4.5 minutes. 

##Future Works
[Back to Table of Contents] (README.md#table-of-contents)

- The current code only implements multithreading on a single machine, to further increase scalability and fault tolerance, we can consider distributed frameworks. I have tested some version of code on spark which didn't perform veru well (using dataframe to store the edges which is easy for the processes like finding second order and 4th order connections -- just a couple of joins). The reason may be spark is not designed for transactions updating and querying.

- The input now is read line by line from the text file. In real application, a streaming technique is neccessary, we can consider kafka as a good framework for streaming. 

- Now the initial graphs are store in python dictionaries which are not scalable. In real application, a good distributed database supporting fast query and transactions (read, write) is of great importance.    
