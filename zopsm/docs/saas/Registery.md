Tenant must register its consumers to the SaaS service by hitting `/register_consumer` endpoint with 
`token`, `project_id`, `service_id` and `consumer_id`(if exists, it can be exist if consumer 
registered once so that it can be able to use one of the other services). Then, SaaS service 
register that consumer to related services. `service_id` can be a list for consumers that use 
multiple services.

