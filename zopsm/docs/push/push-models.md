### Push Models

#### Target

| attr        | description                                      |
| ----------- | ------------------------------------------------ |
| consumer_id | unique identifier of `tenant`'s user.            |
| push_tags   | tags for push service                            |
| token       | target's token obtained from target              |
| tenant      | tenant id of token                               |

#### Segment 

| attr        | description                                         |
| ----------- | ----------------------------------------------------|
| segment_id  | segment_id                                          |
| tenant      | tenant id of token                                  |
| name        | segment name                                        |
| residents   | logical expressions that defines the set of targets |

#### Tag 

| attr        | description                                         |
| ----------- | ----------------------------------------------------|
| key         | tag's key                                           |
| type        | user, or client                                     |

#### Message 

| attr        | description                                           |
| ----------- | ------------------------------------------------------|
| id          | unique identifier of messages                         |
| title       | title of message                                      |
| body        | body of message                                       |
| type        | automated, scheduled, ordinary                        |
| language    | language                                              |
| icon        | icon                                                  |
| image       | image                                                 |
| badge       | badge                                                 |


#### Delivery 


- session?


