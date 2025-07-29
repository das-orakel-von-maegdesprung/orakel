//translations.js
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
    emailStepTitle: "Willkommen beim Orakel von Mägdesprung",

    chatTitle: "Frage das Orakel",
    chatSubtitle: "Stelle deine Frage und erhalte Weisheit aus Mägdesprung",
    oracleLabel: "Orakel:",
    emptyState: "Willkommen! Stelle deine erste Frage an das Orakel von Mägdesprung.",
    typingIndicator: "Orakel denkt nach",
    chatPlaceholder: "Schreibe deine Frage hier...",
    buttonText: "Fragen",
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
    emailStepTitle: "Welcome to the Oracle of Mägdesprung",

    chatTitle: "Ask the Oracle",
    chatSubtitle: "Ask your question and receive wisdom from Mägdesprung",
    oracleLabel: "Oracle:",
    emptyState: "Welcome! Ask your first question to the Oracle of Mägdesprung.",
    typingIndicator: "Oracle is thinking",
    chatPlaceholder: "Write your question here...",
    buttonText: "Ask",
  }
};

function t(key, params = {}, userLang) {
  const lang = translations[userLang] ? userLang : 'en'; // fallback to English if undefined
  let txt = translations[lang][key] || key;
  Object.entries(params).forEach(([k, v]) => {
    txt = txt.replace(`{${k}}`, v);
  });
  return txt;
}


function updateTexts(lang) {
  // Update all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key, {}, lang);
  });
  
  // Update placeholders separately
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = t(key, {}, lang);
  });
  
  // Update flag and label in toggle
  const flag = lang === 'de' ? '🇩🇪' : '🇬🇧';
  const labelKey = lang === 'de' ? 'langGerman' : 'langEnglish';
  document.getElementById('lang-flag').textContent = flag;
  document.getElementById('lang-label').textContent = t(labelKey, {}, lang);
}

document.querySelectorAll('.lang-menu button').forEach(button => {
  button.addEventListener('click', () => {
    const selectedLang = button.getAttribute('data-lang');
    updateTexts(selectedLang);
    
    // Optional: close lang menu or update UI state
    document.getElementById('lang-menu').style.display = 'none';
  });
});
