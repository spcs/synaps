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

* Full Filters: Matches metrics with its dimensions contains all of the filters
* Name Filters: Matches metrics with its dimensions schema 
* Value Filters: Matches metrics with its dimensions at least one of value 
                 contains the filters

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description
   * - Name
     - Name of the dimension that matches.

       Data type: String

       Length limitation: 0 ~ 255 bytes
   * - Value
     - Value of the dimension that matches.
     
       Data type: String

       Length limitation: 0 ~ 255 bytes   