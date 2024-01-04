package org.catalyst.config;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.kafka.streams.StreamsConfig;
import org.postgresql.ds.PGSimpleDataSource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.annotation.EnableKafkaStreams;
import org.springframework.kafka.annotation.KafkaStreamsDefaultConfiguration;
import org.springframework.kafka.config.KafkaStreamsConfiguration;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableKafka
@EnableKafkaStreams
public class ConsumerConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    public String bootstrapServers;
    @Value("${spring.kafka.application-id}")
    public String applicationId;
    @Value("${spring.kafka.auto-offset-reset-config}")
    public String autoOffsetResetConfig;
    @Value("${count.psql.host}")
    public String countPsqlHost;
    @Value("${count.psql.port}")
    public int countPsqlPort;
    @Value("${count.psql.username}")
    public String countPsqlUsername;
    @Value("${count.psql.password}")
    public String countPsqlPassword;
    @Value("${count.psql.database-name}")
    public String countPsqlDBName;
    @Value("${count.schema.file.path}")
    public String countSchemaFilePath;


    @Bean(name = KafkaStreamsDefaultConfiguration.DEFAULT_STREAMS_CONFIG_BEAN_NAME)
    KafkaStreamsConfiguration kStreamsConfig() {
        Map<String, Object> props = new HashMap<>();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, this.applicationId);
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, this.bootstrapServers);
        props.put(org.apache.kafka.clients.consumer.ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, this.autoOffsetResetConfig);
        return new KafkaStreamsConfiguration(props);
    }

    @Bean
    Connection getCountDatabaseConnection () throws SQLException {
        if (this.countPsqlHost.isEmpty() || this.countPsqlDBName.isEmpty())
            return null;
        PGSimpleDataSource dataSource = new PGSimpleDataSource();
        dataSource.setServerNames(new String[]{this.countPsqlHost});
        dataSource.setPortNumbers(new int[]{this.countPsqlPort});
        dataSource.setDatabaseName(this.countPsqlDBName);
        dataSource.setUser(this.countPsqlUsername);
        dataSource.setPassword(this.countPsqlPassword);
        return dataSource.getConnection();
    }
}