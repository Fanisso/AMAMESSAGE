package com.deepseek;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.editor.Document;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import org.jetbrains.annotations.NotNull;

public class DeepSeekAction extends AnAction {
    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        Project project = e.getProject();
        if (project == null) return;
        
        Editor editor = com.intellij.openapi.actionSystem.CommonDataKeys.EDITOR.getData(e.getDataContext());
        if (editor == null) {
            Messages.showInfoMessage("Abra um arquivo primeiro", "DeepSeek");
            return;
        }
        
        Document document = editor.getDocument();
        String language = LanguageSupport.detectLanguage(document);
        
        if (!LanguageSupport.isSupportedLanguage(language)) {
            Messages.showInfoMessage("Linguagem não suportada", "DeepSeek");
            return;
        }
        
        String selectedText = editor.getSelectionModel().getSelectedText();
        String code = selectedText != null ? selectedText : document.getText();
        
        Messages.showInfoMessage("DeepSeek analisará: " + language + " (" + code.length() + " caracteres)", "DeepSeek");
    }
}
