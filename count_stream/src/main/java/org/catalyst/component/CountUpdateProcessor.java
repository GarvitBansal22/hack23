package org.catalyst.component;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.apache.kafka.streams.processor.api.Processor;
import org.apache.kafka.streams.processor.api.ProcessorContext;
import org.apache.kafka.streams.processor.api.Record;
import org.apache.kafka.streams.processor.api.RecordMetadata;
import org.catalyst.util.EnrichProcessor;
import org.catalyst.util.Utility;

import java.sql.Connection;
import java.time.Instant;
import java.util.Optional;

public class CountUpdateProcessor implements Processor<JsonObject, JsonObject, JsonObject, JsonObject> {

    public  Connection countDBConnection;
    private ProcessorContext context;
    public CountUpdateProcessor (Connection countDBConnection) {
        this.countDBConnection = countDBConnection;
    }
    @Override
    public void init(ProcessorContext<JsonObject, JsonObject> context) {
        Processor.super.init(context);
        this.context = context;
    }

    @Override
    public void process(Record<JsonObject, JsonObject> record) {
        String module = null;
        JsonObject message = record.value();
        Optional<RecordMetadata> metaData = context.recordMetadata();
        if (metaData.isPresent()) {
            RecordMetadata recordMetadata = metaData.get();
            String topic = recordMetadata.topic();
            module = Utility.extractModule(topic);
        }
        try {
            EnrichProcessor.getPresentCount(message, module, countDBConnection);
        }
        catch (Exception e) {
            System.out.println(e);
        }
        context.forward(record);
    }

    @Override
    public void close() {
        Processor.super.close();
    }
}
