A set of scripts to set up data replication from GAE Datastore to MySQL.


GAE Datastore data fetcher
----------

#### GET *http://your_app_name.appspot.com/recent_data*

#####params:

* **secret_key** *(required)* *[string]* - The secret key to retrieve data;
* **kind** *(required)* *[string]* - Datastore kind name to download data from;
* **batch_size** *(optional)* *[integer]* - The amount of entities to be downloaded in each request (100 by default);
* **from** *(required)* *[datetime]* - string of format *"YYYY-MM-DD hh:mm:ss"* - The date the downloaded entities were created after;
* **to** *(optional)* *[datetime]* - string of format *"YYYY-MM-DD hh:mm:ss"* - The date the downloaded entities were created before (datetime.now() by default);
* **session_id** *(optional)* *[integer]* - ID of the data retrieving session (0 by default). Should be incremented each time the client wants to download data over again. As long as session_id remains unchanged, the server iterates over the requested table and returns its recently updated data in batches, finishing up its job with a response with 0 entities;
* **repeat_previous** *(optional)* *[string]* - if "True", then the server returns the same batch of entities as in the previous request ("False" by default). Can be used in case there were some errors while processing the previous request on the client side.


MySQL data replication server
----------

*TODO*
