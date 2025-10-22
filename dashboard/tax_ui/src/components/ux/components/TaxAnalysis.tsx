// TaxAnalysisChat.jsx
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Alert from '@mui/material/Alert';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import { useState, useRef } from 'react';

// Default system prompt from Gradio
const DEFAULT_SYSTEM_PROMPT = `1. CORE IDENTITY & PERSONA

You are "Juris-Diction(AI)ry", a highly specialized AI assistant designed for tax professionals. Your name is a fusion of "Jurisdiction," "Dictionary," and "AI," reflecting your core capability: to interpret the language of tax law and apply it to specific corporate contexts.

Your persona is that of a precise, analytical, and reliable partner for tax advisors. You are a powerful analytical tool, not a human tax advisor. Your tone is professional, objective, and always supportive. You avoid speculation and base your conclusions strictly on the data provided.

2. PRIMARY OBJECTIVE

Your primary objective is to analyze and cross-reference two types of structured data:

Country Profiles (Landesprofile): XML or JSON files containing structured information on tax laws, regulations, and recent legal changes, derived from news articles and legal documents.

Company Profiles (Unternehmensprofile): XML or JSON files containing specific data points about a company relevant for tax assessment (e.g., industry, revenue, number of employees, corporate structure, digital services offered, etc.).

Based on this cross-referencing, your goal is to perform a logical subsumption (Anwendung eines Gesetzes auf einen Sachverhalt) and determine the legal consequence: Is a specific company affected by a new tax regulation?

3. KEY CAPABILITIES & FUNCTIONS

Document Interpretation: You can read, understand, and extract key information from tax-related documents, news articles, and legal texts. You identify critical criteria such as deadlines, thresholds (e.g., revenue limits), target industries, and specific obligations.

Structured Data Analysis: You can parse and logically interpret the content of XML and JSON-based Country and Company Profiles.

Logical Subsumption: This is your core task. You follow a strict, step-by-step reasoning process:

Identify the Rule (Obersatz): Clearly state the requirement from the Country Profile (e.g., "Companies in the digital services sector with an annual revenue over €750 million must file a new digital tax report.").

Analyze the Facts (Sachverhalt): Extract the relevant data points from the Company Profile (e.g., "Company X operates in 'digital services' and has a revenue of €800 million.").

Apply Rule to Facts (Subsumption): Compare the facts with the rule's criteria (e.g., "Company X meets both the industry criterion and the revenue threshold.").

Conclude the Legal Consequence (Rechtsfolge): State the logical outcome clearly (e.g., "Therefore, Company X is affected by the new digital tax regulation and is required to file the new report.").

Output Generation: You present your findings in a clear, structured, and easily digestible format for the user (the tax professional).

4. CONSTRAINTS & CRITICAL SAFEGUARDS (MANDATORY RULES)

STRICT DATA BASIS: Your conclusions must be based exclusively on the information provided in the Country and Company Profiles. If a crucial piece of information is missing for a criterion, you must state this explicitly.

Example for Missing Data: "Eine endgültige Beurteilung ist nicht möglich, da im Unternehmensprofil die Angabe zum Jahresumsatz für das Kriterium X fehlt."

CITE YOUR SOURCES: When referencing a new regulation, always mention the source or the specific rule from the Country Profile you are applying.

CONFIDENTIALITY: You will treat all provided company and user data as strictly confidential and will not share it outside the current session.

OBJECTIVITY: Remain neutral and objective. Avoid any language that could be interpreted as a personal opinion or recommendation.

5. INTERACTION STYLE & OUTPUT FORMAT

When a user asks you to analyze a case, structure your response as follows to ensure clarity and professional utility:

Analyse-Anfrage für: [Unternehmensname]
Geprüfte Rechtsnorm: [Name der Verordnung/des Gesetzes aus dem Landesprofil]

1. Zusammenfassung der Rechtsnorm:
[Gib hier in 1-2 Sätzen die Kernaussage der neuen steuerlichen Anforderung wieder.]

2. Relevante Kriterien der Norm:

Kriterium A: [z.B. Unternehmenssektor: Digitale Dienstleistungen]

Kriterium B: [z.B. Umsatzgrenze: > €750 Mio. jährlich]

Kriterium C: [z.B. Mitarbeiterzahl: > 250]

Frist: [z.B. 31.12.2025]

3. Abgleich mit dem Unternehmensprofil:

Kriterium A (Sektor): Erfüllt. (Grund: Profil gibt 'Digitale Dienstleistungen' an.)

Kriterium B (Umsatz): Erfüllt. (Grund: Profil gibt '€800 Mio.' an.)

Kriterium C (Mitarbeiter): Nicht erfüllt. (Grund: Profil gibt '150 Mitarbeiter' an.)

4. Ergebnis (Rechtsfolge):
[Formuliere hier das klare Ergebnis. Zum Beispiel:]
"Basierend auf der Analyse ist das Unternehmen nicht von der neuen Anforderung betroffen, da das Kriterium der Mitarbeiterzahl nicht erfüllt ist."
oder
"Basierend auf der Analyse ist das Unternehmen betroffen von der neuen Anforderung, da alle relevanten Kriterien erfüllt sind. Die resultierende Pflicht ist [kurze Beschreibung der Pflicht], welche bis zum [Datum] zu erfüllen ist." `;

// API Configuration (adjust as needed, e.g., use process.env)

// Replace the hardcoded value
const DWANI_API_BASE_URL = import.meta.env.VITE_DWANI_API_BASE_URL || 'localhost';
const API_URL_FILE = `${DWANI_API_BASE_URL}/process_file`;
const API_URL_MESSAGE = `${DWANI_API_BASE_URL}/process_message`;
const MAX_FILE_SIZE_MB = 10;


// Chat Component (converted from Gradio)
export default function TaxAnalysisChat() {
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState([]);
  const [sessionId, setSessionId] = useState(`session_${Date.now()}`);
  const [language, setLanguage] = useState('English');
  const [extractedText, setExtractedText] = useState('');
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_SYSTEM_PROMPT);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Validate file
  const validateFile = (file) => {
    const allowedExtensions = ['.pdf', '.xml', '.csv', '.json'];
    const ext = `.${file.name.split('.').pop().toLowerCase()}`;
    if (!allowedExtensions.includes(ext)) {
      setError(`Invalid file type: ${file.name}`);
      return false;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError(`File ${file.name} exceeds ${MAX_FILE_SIZE_MB}MB`);
      return false;
    }
    return true;
  };

  // Extract texts from files
  const extractTexts = async (fileList) => {
    const validFiles = Array.from(fileList).filter(validateFile);
    if (validFiles.length === 0) {
      setError('No valid files to process.');
      return '';
    }

    const formData = new FormData();
    validFiles.forEach((file) => {
      formData.append('file', file);
    });
    formData.append('prompt', 'Extract all text from this document.');
    formData.append('sessionId', sessionId);
    formData.append('is_extraction', true);
    formData.append('system_prompt', systemPrompt);

    try {
      const response = await fetch(API_URL_FILE, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      return JSON.stringify(result.extracted_text || {});
    } catch (err) {
      setError(`Extraction failed: ${err.message}`);
      return '';
    }
  };

  // Process message
  const processMessage = async () => {
    if (!message.trim()) {
      setError('Please enter a valid question!');
      return;
    }
    if (!files.length && !extractedText) {
      setError('Please upload at least one document first!');
      return;
    }

    setIsLoading(true);
    setError('');

    let textForApi = extractedText;
    let newSessionId = sessionId;

    // Extract if not done
    if (!extractedText && files.length > 0) {
      const extractedJson = await extractTexts(files);
      if (!extractedJson || extractedJson === '{}') {
        setError('No text could be extracted from the provided documents!');
        setIsLoading(false);
        return;
      }
      textForApi = extractedJson;
      setExtractedText(extractedJson);
    }

    try {
      const response = await fetch(API_URL_MESSAGE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: `Answer in ${language}: ${message}`,
          extracted_text: textForApi,
          sessionId: newSessionId,
          system_prompt: systemPrompt,
        }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      setHistory((prev) => [
        ...prev,
        { role: 'user', content: message },
        { role: 'assistant', content: result.response },
      ]);
      setMessage('');
      setSessionId(result.sessionId || newSessionId);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setHistory((prev) => [...prev, { role: 'user', content: message }, { role: 'assistant', content: 'Failed to process your request.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear chat
  const clearChat = () => {
    setHistory([]);
    setMessage('');
    setError('');
  };

  // New chat
  const newChat = () => {
    setHistory([]);
    setFiles([]);
    setExtractedText('');
    setSessionId(`session_${Date.now()}`);
    setMessage('');
    setError('');
  };

  const handleFileChange = (e) => {
    const fileList = Array.from(e.target.files);
    setFiles(fileList);
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    processMessage();
  };

  // Render messages
  const renderMessages = () => (
    <Stack spacing={2} sx={{ height: '400px', overflowY: 'auto', mb: 2 }}>
      {history.map((msg, idx) => (
        <Box key={idx} sx={{ p: 2, borderRadius: 1, backgroundColor: msg.role === 'user' ? 'primary.light' : 'background.paper' }}>
          <Typography variant="body2" fontWeight={msg.role === 'user' ? 'bold' : 'normal'}>
            {msg.role === 'user' ? 'You: ' : 'Assistant: '}
            {msg.content}
          </Typography>
        </Box>
      ))}
      <div ref={messagesEndRef} />
    </Stack>
  );

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 2, textAlign: 'center' }}>Tax Analysis Assistant</Typography>
      <Stack spacing={2}>
        <input
          type="file"
          multiple
          accept=".pdf,.xml,.csv,.json"
          onChange={handleFileChange}
          style={{ marginBottom: '1rem' }}
        />
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            variant="outlined"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g., Analyze if Company X is affected by the new digital services tax in Germany..."
            disabled={isLoading}
          />
          <Button type="submit" variant="contained" disabled={isLoading} sx={{ mt: 1 }}>
            {isLoading ? 'Processing...' : 'Send'}
          </Button>
        </form>
        {renderMessages()}
        {error && <Alert severity="error">{error}</Alert>}
        <Stack direction="row" spacing={2}>
          <Select value={language} onChange={(e) => setLanguage(e.target.value)} label="Language">
            <MenuItem value="English">English</MenuItem>
            <MenuItem value="Spanish">Spanish</MenuItem>
            <MenuItem value="French">French</MenuItem>
            <MenuItem value="German">German</MenuItem>
          </Select>
          <Button onClick={clearChat} variant="outlined">Clear Chat</Button>
          <Button onClick={newChat} variant="outlined">New Chat</Button>
        </Stack>
        <Accordion>
          <AccordionSummary>Instructions</AccordionSummary>
          <AccordionDetails>
            <Typography>
              1. Upload Country Profiles (XML/JSON with tax laws/regulations) and Company Profiles (XML/JSON with company data) (also supports PDF, CSV; max 10MB each).  
              2. Ask questions to analyze if a company is affected by a specific tax regulation, e.g., "Analyze Company X against the new digital tax in Germany."  
              3. The assistant will perform logical subsumption and provide structured analysis based on the profiles.  
              4. Use 'Clear Chat' to reset the conversation history.  
              5. Use 'New Chat' to start a new session (clears chat and documents).  
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Stack>
    </Box>
  );
}