# Graph-Coloring-Using-Quantum-Computing
Solving the general planar graph colouring problem using Grover's Algorithm. The backtracking algorithm takes O(k^n) for k colours and n vertices while Grover's reduces this complexity to O(sqrt(k^n)) providing a quadratic speedup.

Given 4 nodes to be coloured using 4 colours, we represent each colour using 2 binary bits and build the quantum circuit to apply the Grover search algorithm for proper colouring.

![image](https://github.com/user-attachments/assets/7d5005c5-d6de-4c29-87e5-0c1d37a19413)



We visualize the results in the histogram and look for the most likely outcomes which will give us the proper colouring of the graph:

![download (7)](https://github.com/user-attachments/assets/ea81ca61-47e1-4c7b-bfce-d6565f95e3e9)


Finally, we convert the binary strings to the corresponding coloring.
![image](https://github.com/user-attachments/assets/af31e9ba-220a-48ac-8a03-332bdea0ea4b)





