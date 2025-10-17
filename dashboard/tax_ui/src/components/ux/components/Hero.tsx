import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid2';
import Divider from '@mui/material/Divider';
import { styled } from '@mui/material/styles';
import Chip from '@mui/material/Chip';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Alert from '@mui/material/Alert';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import {
  GavelOutlined,
  DocumentScannerOutlined,
  TimelineOutlined,
  BusinessOutlined,
  AssessmentOutlined,
} from '@mui/icons-material';
import { useState, useRef } from 'react';

// Styled FeatureCard (unchanged from your original code)
const FeatureCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[2],
  textAlign: 'center',
  transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
  '&:hover': {
    transform: 'scale(1.05)',
    boxShadow: theme.shadows[4],
  },
  '&:focus-within': {
    transform: 'scale(1.05)',
    boxShadow: theme.shadows[4],
    outline: `2px solid ${theme.palette.primary.main}`,
  },
}));

// Styled Problem/Solution Card
const ProblemSolutionCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
  transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: theme.shadows[6],
  },
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  minHeight: '200px',
  textAlign: 'center',
}));

// Data for Problem and Solution sections based on PDF
const problems = [
  {
    text: 'High time effort for manual research required',
    icon: <TimelineOutlined color="error" fontSize="large" />,
    chipLabel: 'Time',
  },
  {
    text: 'Company becomes vulnerable if it is not up to date legally',
    icon: <GavelOutlined color="error" fontSize="large" />,
    chipLabel: 'Legal',
  },
  {
    text: 'Implementation hurdles make an early project start necessary',
    icon: <BusinessOutlined color="error" fontSize="large" />,
    chipLabel: 'Execute',
  },
  {
    text: 'Politics may turn legal monitoring into a crisis',
    icon: <AssessmentOutlined color="error" fontSize="large" />,
    chipLabel: 'Politics',
  },
];

const solutions = [
  {
    text: 'From Obligation to Strategy: Proactive Selling of Services',
    icon: <GavelOutlined color="primary" fontSize="large" />,
    chipLabel: 'For Tax Advisors',
  },
  {
    text: 'Unbeatable Client Retention and No More Surprises',
    icon: <BusinessOutlined color="primary" fontSize="large" />,
    chipLabel: 'Client Retention',
  },
  {
    text: 'Efficient Resource Planning and Comprehensive Compliance Assurance',
    icon: <DocumentScannerOutlined color="primary" fontSize="large" />,
    chipLabel: 'For Corporations',
  },
  {
    text: 'Paradigm shift from reactive legal function to proactive business partner',
    icon: <TimelineOutlined color="primary" fontSize="large" />,
    chipLabel: 'Proactive Shift',
  },
];

const features = [
  {
    title: 'E-Invoicing Obligation',
    description: 'AI Workflow: Detect, Understand, Apply to generate client alerts in 24 hours.',
    components: 'Legal Monitoring',
    hardware: 'GPU',
  },
  {
    title: 'Transfer Pricing',
    description: 'Upcoming module for proactive compliance in international tax strategies.',
    components: 'Tax Agent',
    hardware: 'CPU/GPU',
  },
  {
    title: 'Pillar 2 & ESG Reporting',
    description: 'Scalable alerts for global tax standards and sustainability reporting.',
    components: 'Dashboard',
    hardware: 'GPU',
  },
  {
    title: 'Labor Law, GDPR, Contract Law',
    description: 'Expandable to other legal domains with document parsing and communication profiles.',
    components: 'Multimodal',
    hardware: 'CPU/GPU',
  },
];

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
const DWANI_API_BASE_URL = '0.0.0.0'; // From env in production
const API_URL_FILE = `http://${DWANI_API_BASE_URL}:8000/process_file`;
const API_URL_MESSAGE = `http://${DWANI_API_BASE_URL}:8000/process_message`;
const API_URL_HEALTH = `http://${DWANI_API_BASE_URL}:8000/health`;
const MAX_FILE_SIZE_MB = 10;

// Chat Component (converted from Gradio)
function TaxAnalysisChat() {
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

// Main Hero Component (integrated chat replacing <UserApp/>)
export default function Hero() {
  return (
    <>
      <title>Juris-Diction(AI)ry | AI-Powered Legal Monitoring</title>
      <meta
        name="description"
        content="Discover Juris-Diction(AI)ry, powered by dwani.ai – a GenAI platform for proactive legal monitoring in tax and beyond. From E-Invoicing to ESG, ensure compliance with secure, multimodal analytics."
      />
      <meta
        name="keywords"
        content="Juris-Diction(AI)ry, dwani.ai, legal monitoring, tax compliance, E-Invoicing, Transfer Pricing, Pillar 2, ESG Reporting, AI legal alerts"
      />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="robots" content="index, follow" />
      <link rel="canonical" href="https://uberTax" />

      <Box
        id="hero"
        role="banner"
        sx={(theme) => ({
          width: '100%',
          backgroundRepeat: 'no-repeat',
          backgroundImage:
            'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 90%), transparent)',
          ...theme.applyStyles('dark', {
            backgroundImage:
              'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 16%), transparent)',
          }),
          py: { xs: 8, sm: 12 },
        })}
      >
        <Container
          maxWidth="lg"
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            pt: { xs: 10, sm: 16 },
            pb: { xs: 6, sm: 10 },
          }}
        >
          <Stack
            spacing={3}
            useFlexGap
            sx={{ alignItems: 'center', width: { xs: '100%', sm: '80%', md: '60%' } }}
          >
            <Typography
              variant="h1"
              component="h1"
              sx={{
                fontSize: 'clamp(2.5rem, 7vw, 3.75rem)',
                fontWeight: 'bold',
                color: 'primary.main',
                textAlign: 'center',
              }}
            >
              Juris-Diction(AI)ry
            </Typography>
            <Typography
              variant="h6"
              component="h2"
              sx={{
                textAlign: 'center',
                color: 'text.secondary',
                fontWeight: 'medium',
              }}
            >
              Powered by dwani.ai
            </Typography>

            <Divider sx={{ width: '60%', mx: 'auto', my: 2 }} />

            <Typography
              variant="body1"
              sx={{ textAlign: 'center', color: 'text.secondary' }}
            >
              Proactive Legal Monitoring: From Crisis to Strategic Advantage
            </Typography>

            <Button
              variant="contained"
              color="primary"
              href="https://app.dwani.ai"
              target="_blank"
              size="large"
              sx={{ mt: 2, px: 4, py: 1.5, borderRadius: 2 }}
              aria-label="Try Juris-Diction on dwani.ai"
            >
              Try Legal Monitoring
            </Button>

            <Divider sx={{ width: '60%', mx: 'auto', my: 2 }} />

            <Typography
              variant="body1"
              sx={{ textAlign: 'center', color: 'text.secondary' }}
            >
              From Concept to Live Alerts in 24 Hours. Explore the{' '}
              <Link
                href="https://docs.dwani.ai/"
                target="_blank"
                color="primary"
                aria-label="dwani.ai documentation"
              >
                Documentation
              </Link>.
            </Typography>

            <Button
              variant="contained"
              color="primary"
              href="https://workshop.dwani.ai"
              target="_blank"
              size="large"
              sx={{ mt: 2, px: 4, py: 1.5, borderRadius: 2 }}
              aria-label="Try Multimodal Inference for Legal Docs"
            >
              Try - AI Workflow
            </Button>

            <Divider sx={{ width: '60%', mx: 'auto', my: 2 }} />

            {/* Problem Section */}
            <Stack
              spacing={4}
              useFlexGap
              sx={{ alignItems: 'center', width: '100%', mt: 8 }}
            >
              <Typography
                variant="h4"
                component="h3"
                sx={{ textAlign: 'center', fontWeight: 'bold' }}
              >
                Legal Monitoring is a Critical Pain Point
              </Typography>
              <Grid container spacing={3}>
                {problems.map((problem, index) => (
                  <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
                    <ProblemSolutionCard tabIndex={0}>
                      <Box sx={{ mb: 2 }}>{problem.icon}</Box>
                      <Typography
                        variant="body2"
                        sx={{ color: 'text.secondary', mb: 1 }}
                      >
                        {problem.text}
                      </Typography>
                      <Chip
                        label={problem.chipLabel}
                        color="error"
                        variant="outlined"
                        size="small"
                      />
                    </ProblemSolutionCard>
                  </Grid>
                ))}
              </Grid>
            </Stack>

            {/* Solution Section */}
            <Stack
              spacing={4}
              useFlexGap
              sx={{ alignItems: 'center', width: '100%', mt: 6 }}
            >
              <Typography
                variant="h4"
                component="h3"
                sx={{ textAlign: 'center', fontWeight: 'bold' }}
              >
                The Dual-Benefit Solution
              </Typography>
              <Grid container spacing={3}>
                {solutions.map((solution, index) => (
                  <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
                    <ProblemSolutionCard tabIndex={0}>
                      <Box sx={{ mb: 2 }}>{solution.icon}</Box>
                      <Typography
                        variant="body2"
                        sx={{ color: 'text.secondary', mb: 1 }}
                      >
                        {solution.text}
                      </Typography>
                      <Chip
                        label={solution.chipLabel}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                    </ProblemSolutionCard>
                  </Grid>
                ))}
              </Grid>
            </Stack>
          </Stack>

          {/* Features Section */}
          <Stack
            spacing={4}
            useFlexGap
            sx={{ alignItems: 'center', width: '100%', mt: 8 }}
          >
            <Typography
              variant="h4"
              component="h2"
              sx={{ textAlign: 'center', fontWeight: 'bold' }}
            >
              Scalable Modules & Workflow
            </Typography>
            <Grid container spacing={3}>
              {features.map((feature, index) => (
                <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
                  <FeatureCard tabIndex={0}>
                    <Typography variant="h6" sx={{ fontWeight: 'medium' }}>
                      {feature.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ color: 'text.secondary', mt: 1 }}
                    >
                      {feature.description}
                    </Typography>
                    <Stack
                      direction="row"
                      spacing={1}
                      sx={{ mt: 2, justifyContent: 'center' }}
                    >
                      <Chip
                        label={feature.components}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                      <Chip
                        label={feature.hardware}
                        color="secondary"
                        variant="outlined"
                        size="small"
                      />
                    </Stack>
                  </FeatureCard>
                </Grid>
              ))}
            </Grid>
          </Stack>

          {/* Integrated Tax Analysis Chat (replaces <UserApp/>) */}
          <TaxAnalysisChat />

          {/* Contact Section */}
          <Stack
            spacing={2}
            useFlexGap
            sx={{ alignItems: 'center', width: '100%', mt: 8 }}
          >
            <Divider sx={{ width: '60%', mx: 'auto', my: 2 }} />
            <Typography
              variant="h4"
              component="h2"
              sx={{ textAlign: 'center', fontWeight: 'bold' }}
            >
              Get in Touch
            </Typography>
            <Typography
              variant="body1"
              sx={{ textAlign: 'center', color: 'text.secondary' }}
            >
              Join our{' '}
              <Link
                href="https://discord.gg/9Fq8J9Gnz3"
                target="_blank"
                color="primary"
                aria-label="Join dwani.ai Discord community"
              >
                Discord community
              </Link>{' '}
              for collaborations.
              <br />
              Have questions?{' '}
              <Link
                href="https://calendar.app.google/j1L2Sh6sExfWpUTZ7"
                target="_blank"
                color="primary"
                aria-label="Schedule a demo with dwani.ai"
              >
                Schedule a Demo
              </Link>.
            </Typography>
          </Stack>
        </Container>
      </Box>
    </>
  );
}