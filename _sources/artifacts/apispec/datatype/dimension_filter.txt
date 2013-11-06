.. _dimension_filter:

DimensionFilter
===============

Description
-----------
Search condition to be applied to :ref:`list_metrics`.

Contents
--------

Following is contents of this data type.

There are three types of dimension filter.

1. Full Filter(specifying both Name and Value) returns metrics if its dimensions 
contains the filters.

2. Name Filter(specifying a Name without specifying a Value) returns metrics if 
its dimensions schema matches. 
 
3. Value Filters(specifying a Value without specifying a Name) returns metrics 
when at least one value of its dimensions contains the filter value.

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description
   * - Name
     - The dimension name to be matched.

       Data type: String

       Length limitation: 0 ~ 255 bytes
   * - Value
     - The dimension value to be matched.

       Data type: String

       Length limitation: 0 ~ 255 bytes