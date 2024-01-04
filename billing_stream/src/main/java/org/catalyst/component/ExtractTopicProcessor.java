package org.catalyst.component;

import com.google.gson.JsonObject;
import org.apache.kafka.streams.processor.api.Processor;
import org.apache.kafka.streams.processor.api.ProcessorContext;
import org.apache.kafka.streams.processor.api.Record;
import org.apache.kafka.streams.processor.api.RecordMetadata;
import org.catalyst.util.Utility;

import java.time.Instant;
import java.util.Optional;

public class ExtractTopicProcessor  implements Processor<JsonObject, JsonObject, JsonObject, JsonObject> {

    private ProcessorContext context;

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
            message.addProperty("module_name", module);
        }
        Record<JsonObject, JsonObject> updatedRecord = new Record<>(record.key(), message, Instant.now().toEpochMilli());
        context.forward(updatedRecord);
    }

    @Override
    public void close() {
        Processor.super.close();
    }
}
