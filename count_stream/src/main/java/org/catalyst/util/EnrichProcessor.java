package org.catalyst.util;

import com.google.gson.JsonObject;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

public class EnrichProcessor {
    public static void getPresentCount(JsonObject jsonObject, String module, Connection connection) throws IllegalArgumentException, SQLException {
        String query = "SELECT * from monthly_counts";
        long dateEpoche = jsonObject.get(Constants.CREATED_MAPPING.get(module)).getAsLong();
        Instant instant = Instant.ofEpochMilli(dateEpoche/1000);
        LocalDateTime dateTime = LocalDateTime.ofInstant(instant, ZoneId.of("UTC"));
        setVendor(jsonObject, module);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM");
        String monthYearString = dateTime.format(formatter);
        jsonObject.addProperty("month_year_string", monthYearString);
        String where = Utility.getCountWhereClause(jsonObject, monthYearString, Constants.MODULE_KEY_MAPPING.get(module));
        if (where.isEmpty())
            throw new IllegalArgumentException("where can't be null");
        query = query + " where " + where;
        Statement statement = connection.createStatement();
        ResultSet resultSet = statement.executeQuery(query);
        if (resultSet.next()) {
            String update_query = "UPDATE monthly_counts SET message_count_monthly = message_count_monthly + 1 where " + where;
            statement.executeQuery(update_query);
        }
        else {
            String insertQuery = "INSERT INTO monthly_counts (company_id, vendor, month_year_string, message_count_monthly, mode) VALUES ('"+jsonObject.get("company_id").getAsString()+"', '"+jsonObject.get("vendor").getAsString()+"', '"+monthYearString+"', 1, '"+module+"')";
            statement.executeQuery(insertQuery);
        }
    }

    private static void setVendor (JsonObject jsonObject, String module) {
        try{
            String vendor = Utility.getString(jsonObject, "vendor", null);
            if (vendor == null)
                throw new Exception();
        }
        catch (Exception e) {
            if (module.equals("call")) {
//                JsonObject commDict = Utility.getJson(jsonObject, "comm_dict", new JsonObject());
                jsonObject.addProperty("vendor", Utility.getString(jsonObject, "vendor_id", ""));
            }
            else
                jsonObject.addProperty("vendor", "");
        }
    }
}
