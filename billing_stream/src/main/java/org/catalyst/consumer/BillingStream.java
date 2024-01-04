package org.catalyst.consumer;

import com.google.gson.JsonObject;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.processor.RecordContext;
import org.apache.kafka.streams.processor.TopicNameExtractor;
import org.apache.log4j.Logger;
import org.catalyst.component.CountUpdateProcessor;
import org.catalyst.component.ExtractTopicProcessor;
import org.catalyst.util.Constants;
import org.catalyst.util.Utility;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

import java.sql.Connection;
import java.util.regex.Pattern;

@Component
public class BillingStream {

    @Value("${spring.kafka.in-topic-pattern}")
    public String inTopicsRegex;
    @Value("${spring.kafka.out-topic-prefix}")
    public String outTopicPrefix;
    @Value("${spring.kafka.is-schema-enabled}")
    public boolean isSchemaEnabled;
    @Autowired(required=false)
    @Qualifier("getCountDatabaseConnection")
    public Connection countDBConnection;

    private final Logger logger = Logger.getLogger(BillingStream.class);

    @Bean
    public KStream<JsonObject, JsonObject> kStream(StreamsBuilder streamsBuilder) {
        try {
            Pattern topicPattern = Pattern.compile(this.inTopicsRegex);

            TopicNameExtractor<JsonObject , JsonObject> topicNameExtractor = this::getSinkTopic;

            KStream<JsonObject, JsonObject> transformationStream = streamsBuilder
                    .stream(topicPattern, Consumed.with(Utility.jsonSerde(), Utility.jsonSerde()))
                    .process(ExtractTopicProcessor::new)
                    .filter((key,value) -> this.isMessageToBeProcessed(value))
                    .process(() -> new CountUpdateProcessor(countDBConnection));
            transformationStream.to(topicNameExtractor, Produced.with(Utility.jsonSerde(), Utility.jsonSerde()));

            return transformationStream;
        } catch (Exception e) {
            logger.error("Exception occurred while initializing stream : " + e.getMessage());
            return null;
        }
    }

    private boolean isMessageToBeProcessed (JsonObject value){
        String module = Utility.getString(value, "module_name", null);
        if (module == null)
            return false;
        if (Constants.NOTICE_DEPENDENT_COMM.contains(module)) {
            Utility.stringToJson(value, Constants.NOTICE_KEY_MAPPING.get(module));
            boolean flag = true;
            for (String key : Constants.NOTICE_KEY_MAPPING.get(module)) {
                if (value.has(key) && value.get(key).isJsonObject() && !value.get(key).getAsJsonObject().entrySet().isEmpty()){
                    flag = false;
                    break;
                }
            }
            return flag;
        }
        return false;
    }

    private String getSinkTopic (JsonObject key, JsonObject value, RecordContext recordContext){
        String topic = Utility.extractModule(recordContext.topic());
        logger.info("Message produced");
        return this.outTopicPrefix+topic;
    }
}