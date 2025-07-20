// shared translations and helper function
const translations = {
  de: {
    welcome: "Willkommen beim Orakel von Mägdesprung",
    enterEmail: "Deine E-Mail",
    emailRequired: "Bitte eine gültige E-Mail eingeben.",
    emailSent: "Der Login-Code wurde gesendet!",
    enterCode: "6-stelliger Code",
    codeRequired: "Bitte den Code eingeben.",
    invalidCode: "Ungültiger oder abgelaufener Code.",
    codeInfo: "Ein Login-Code wurde an {email} gesendet.",
    next: "Weiter →",
    prev: "← Zurück",
    otherPlaceholder: "Andere Antwort hier eingeben...",
    answersSaved: "Antworten gespeichert. Danke!",
    errorSave: "Fehler beim Speichern der Antworten.",
    errorLoadQuestions: "Fehler beim Laden der Fragen.",
    questionProgress: "Frage {current} von {total}",
    langGerman: "Deutsch",
    langEnglish: "English",
    selectAnswer: "Antwort auswählen",
    languageOverlayTitle: "Willkommen! / Welcome!",
    languagePrompt: "Bitte wähle eine Sprache / Please select a language",
    emailStepTitle: "Willkommen beim Orakel von Mägdesprung"
  },
  en: {
    welcome: "Welcome to the Oracle of Mägdesprung",
    enterEmail: "Your email",
    emailRequired: "Please enter a valid email.",
    emailSent: "Login code sent!",
    enterCode: "6-digit code",
    codeRequired: "Please enter the code.",
    invalidCode: "Invalid or expired code.",
    codeInfo: "A login code has been sent to {email}.",
    next: "Next →",
    prev: "← Back",
    otherPlaceholder: "Enter other answer here...",
    answersSaved: "Answers saved. Thank you!",
    errorSave: "Error saving answers.",
    errorLoadQuestions: "Error loading questions.",
    questionProgress: "Question {current} of {total}",
    langGerman: "German",
    langEnglish: "English",
    selectAnswer: "Select answer",
    languageOverlayTitle: "Welcome! / Willkommen!",
    languagePrompt: "Please select a language / Bitte wähle eine Sprache",
    emailStepTitle: "Welcome to the Oracle of Mägdesprung"
  }
};

function t(key, params = {}, userLang) {
  let txt = translations[userLang][key] || key;
  Object.entries(params).forEach(([k, v]) => {
    txt = txt.replace(`{${k}}`, v);
  });
  return txt;
}
