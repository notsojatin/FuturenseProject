# FuturenseProject


Zookeeper connection: zookeeper-server-start.bat ../../config/zookeeper.properties


start kafka server : kafka-server-start.bat ../../config/server.properties


Producer Topic Creation (Topic1) : kafka-topics.bat --create --topic stockTopic --zookeeper localhost:2181 --partitions 10 --replication-factor 4
Spark Streaming Topic Creation (Topic2) : kafka-topics.bat --create --topic transformedStockTopic --zookeeper localhost:2181 --partitions 10 --replication-factor 4
(for 4 node cluster use replication factor as 4 otherwise adjust as per available node)

Topic1 Describe : kafka-topics.bat --describe --topic stockTopic --zookeeper localhost:2181
Topic2 Describe : kafka-topics.bat --describe --topic transformedStockTopic --zookeeper localhost:2181


Producer Start: kafka-console-producer.bat --broker-list localhost:9092 --topic stockTopic


Consumer Start for Topic1: kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic stockTopic
Consumer Start for Topic2: kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic transformedStockTopic
