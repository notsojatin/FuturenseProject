# FuturenseProject


Zookeeper connection: zookeeper-server-start.bat ../../config/zookeeper.properties\n
start kafka server : kafka-server-start.bat ..\..\config\server.properties\n
Topic Creation : kafka-topics.bat --create --topic stockTopic --zookeeper localhost:2181 --partitions 3 --replication-factor 3\n
Topic Describe : kafka-topics.bat --describe --topic stockTopic --zookeeper localhost:2181\n
Producer Start: kafka-console-producer.bat --broker-list localhost:9092 --topic stockTopic\n
Consumer Satrt: kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic stockTopic --from-beginning\n
