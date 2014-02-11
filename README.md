SocialAdvertiser 
================

Social Advertiser - A Social Network based Advertisement System  (Cooperated with Hakkı Caner Kırmızı and Elsa Liew)

- socialad-recommendation-hadoop
   
   Mapper and Reducer to compute the interest vector of each user and result vector for each recommendation.

- socialadvertiser-django
   
   python code and Django web framework for the front-end service.


This system aims to recommend eligible social network users to product owners who are willing to advertise using the benefits of social media. We used a ranking technique along with a pre-computed ScoreMap which maps the social network user’s interests to product’s related industry based on percentage scale. The most important characteristic of Social Advertiser’s ranking algorithm is that it computes social network user’s rank according to the user’s interests, the relation of these interests with the related industry of advertisement and number of contacts of the user. Social Advertiser, as a system, runs on a parallelized computation environment with three-node Hadoop MapReduce servers. We also compose a technical report to show that why we choose our design from the study into three parts: Registration and Interaction Design, recommendation model, and Processing Large Dataset. Finally, Social Advertiser achieves the positive results as the conclusion claimed.
