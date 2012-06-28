.. _dimension_filter:

Dimension Filter
======================

설명
----
The DimensionFilter data type is used to filter :ref:`list_metrics` results.

Contents
----

.. list-table:: 
   :widths: 15 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - Name
     - The dimension name to be matched.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - Value
     - The value of the dimension to be matched.
     
       Note
         Specifying a Name without specifying a Value returns all values 
         associated with that Name.
         
       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
       
.. toctree::
   :maxdepth: 1 
   