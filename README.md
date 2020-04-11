# PrunedLandmarkLabeling

* Usage
  * Build Index
    * python pll.py build -m [map_file_name] -o [order_mode]
      * map_file_name: The map file downloaded by osmnx
      * order_mode: specify the way to build the vectice order
        * 0: test order, that means the vectices ordered Sequentially
        * 1: degree-based order, that means the vectices ordered by the degree of vectex descending
        * 2: betweeness-based order, that means the vectices ordered by the betweeness of vectex descending
    * Addition Feature
      * -m: use multi-thread.
  * Query distance
    * python pll.py query -s [src_vertex] -t [target_vectex]
      * src_vertex: the source vertex of the query
      * target_vectex: the target vertex of the query
  * Algorithm Validation
    * python pll.py test -t [times] -m [map_file]
      * times: specify the number of validation cases
      * map_file: the map_file of the built index
