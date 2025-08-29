package com.deepseek;

import com.intellij.openapi.editor.Document;
import com.intellij.openapi.fileEditor.FileDocumentManager;
import com.intellij.openapi.vfs.VirtualFile;

public class LanguageSupport {
    public static String detectLanguage(Document document) {
        VirtualFile file = FileDocumentManager.getInstance().getFile(document);
        if (file != null) {
            String extension = file.getExtension();
            if (extension != null) {
                switch (extension.toLowerCase()) {
                    case "java": return "java";
                    case "py": return "python";
                    case "js": return "javascript";
                    case "html": return "html";
                    case "css": return "css";
                }
            }
        }
        return "unknown";
    }
    
    public static boolean isSupportedLanguage(String language) {
        return !"unknown".equals(language);
    }
}
