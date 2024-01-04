package org.catalyst.util;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serializer;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Utility {
    public static Serde<JsonObject> jsonSerde () {
        Gson gson = new Gson();
        Serializer<JsonObject> serializer = (topic, data) -> gson.toJson(data).getBytes();
        Deserializer<JsonObject> deserializer = (topic, data) -> {
            try{
                return gson.fromJson(new String(data), JsonObject.class);
            }
            catch (Exception e) {
                return new JsonObject();
            }
        };
        return Serdes.serdeFrom(serializer, deserializer);
    }
    public static String extractModule (String module) {
        List<String> list = Arrays.asList(module.split("\\."));
        String final_module = list.get(list.size() - 1);
        if (final_module.equals("communication"))
            return  "call";
        return final_module;
    }

    public static String getString(JsonObject jsonObject, String key, String defaultValue){
        try {
            return  jsonObject.get(key).getAsString();
        }
        catch (Exception e){
            return  defaultValue;
        }
    }

    public static JsonObject getJson(JsonObject jsonObject, String key, JsonObject defaultValue){
        try {
            return  jsonObject.get(key).getAsJsonObject();
        }
        catch (Exception e){
            return defaultValue;
        }
    }

    public static String getCountWhereClause (JsonObject jsonObject, String date ,List<String> columns) throws IllegalArgumentException {
        List<String> whereList = new ArrayList<>();
        for (String column : columns) {
            String value = getString(jsonObject, column, null);
            if (value == null)
                throw new IllegalArgumentException("Value not found for column : "+column);
            whereList.add(column + " = '" + value + "'");
        }
        if (date == null)
            throw new IllegalArgumentException("Value not found for column : date");
        whereList.add("month_year_string = '" + date + "'");
        return String.join(" and ", whereList);
    }

    private static void epochToEpochMilli (JsonObject jsonObject, String key){
        if (!jsonObject.has(key) || jsonObject.get(key).isJsonNull() || jsonObject.get(key) == null) {
            jsonObject.add(key, null);
        }
        long value = jsonObject.get(key).getAsLong();
        long updateValue;
        if (value < 100_000_000_000L)
            updateValue = value * 1000;
        else if (value < 100_000_000_000_000L)
            updateValue = value;
        else
            updateValue = value/1000;
        jsonObject.addProperty(key, updateValue);
    }

    public static boolean isDebeziumToast (JsonElement jsonElement) {
        try {
            if (jsonElement.getAsString().equals(Constants.DEBEZIUM_TOAST))
                return true;
            return false;
        } catch (Exception e) {
            return false;
        }
    }

    public static void stringToJson (JsonObject jsonObject, List<String> keys){
        for(String key : keys) {
            if (isDebeziumToast(jsonObject.get(key)))
                jsonObject.addProperty(key, Constants.DEBEZIUM_TOAST);
            else if (jsonObject.has(key) && jsonObject.get(key).isJsonPrimitive() && jsonObject.get(key).getAsJsonPrimitive().isString()){
                try{
                    Gson gson = new Gson();
                    jsonObject.add(key, gson.fromJson(jsonObject.get(key).getAsString(), JsonObject.class));
                } catch (Exception e) {
                    jsonObject.add(key, null);
                }
            }
            else
                jsonObject.add(key, null);
        }
    }
}