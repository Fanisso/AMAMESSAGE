package com.deepseek;

import okhttp3.*;
import java.io.IOException;

public class DeepSeekService {
    private static final String API_URL = "https://api.deepseek.com/v1/chat/completions";
    private final OkHttpClient client = new OkHttpClient();
    
    public String sendRequest(String code, String language) throws IOException {
        String prompt = createLanguageSpecificPrompt(code, language);
        
        String jsonBody = "{\"model\":\"deepseek-coder\",\"messages\":[{\"role\":\"user\",\"content\":\"" + 
                         prompt.replace("\"", "\\\"") + "\"}]}";
        
        Request request = new Request.Builder()
            .url(API_URL)
            .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
            .addHeader("Authorization", "Bearer YOUR_API_KEY")
            .build();
            
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        }
    }
    
    private String createLanguageSpecificPrompt(String code, String language) {
        switch (language.toLowerCase()) {
            case "python": return "Analyze Python: " + code;
            case "java": return "Analyze Java: " + code;
            case "javascript": return "Analyze JS: " + code;
            default: return "Analyze: " + code;
        }
    }
}
