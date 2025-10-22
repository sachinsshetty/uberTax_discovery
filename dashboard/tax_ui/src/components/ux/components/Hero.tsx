// Hero.jsx (updated to only contain informational content)
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
import {
  GavelOutlined,
  DocumentScannerOutlined,
  TimelineOutlined,
  BusinessOutlined,
  AssessmentOutlined,
} from '@mui/icons-material';

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
    text: 'Hoher Zeitaufwand für manuelle Recherche erforderlich',
    icon: <TimelineOutlined color="error" fontSize="large" />,
    chipLabel: 'Zeit',
  },
  {
    text: 'Unternehmen wird verwundbar, wenn es rechtlich nicht auf dem neuesten Stand ist',
    icon: <GavelOutlined color="error" fontSize="large" />,
    chipLabel: 'Rechtlich',
  },
  {
    text: 'Umsetzungshürden erfordern einen frühen Projektstart',
    icon: <BusinessOutlined color="error" fontSize="large" />,
    chipLabel: 'Ausführen',
  },
  {
    text: 'Politik kann rechtliche Überwachung zu einer Krise machen',
    icon: <AssessmentOutlined color="error" fontSize="large" />,
    chipLabel: 'Politik',
  },
];

const solutions = [
  {
    text: 'Von Verpflichtung zur Strategie: Proaktiver Verkauf von Dienstleistungen',
    icon: <GavelOutlined color="primary" fontSize="large" />,
    chipLabel: 'Für Steuerberater',
  },
  {
    text: 'Unübertroffene Kundenbindung und keine Überraschungen mehr',
    icon: <BusinessOutlined color="primary" fontSize="large" />,
    chipLabel: 'Kundenbindung',
  },
  {
    text: 'Effiziente Ressourcenplanung und umfassende Compliance-Sicherstellung',
    icon: <DocumentScannerOutlined color="primary" fontSize="large" />,
    chipLabel: 'Für Unternehmen',
  },
  {
    text: 'Paradigmenwechsel von reaktiver Rechtsabteilung zu proaktivem Geschäftspartner',
    icon: <TimelineOutlined color="primary" fontSize="large" />,
    chipLabel: 'Proaktiver Wandel',
  },
];

const features = [
  {
    title: 'E-Rechnungsverpflichtung',
    description: 'KI-Workflow: Erkennen, Verstehen, Anwenden zur Generierung von Kundenwarnungen in 24 Stunden.',
    components: 'Rechtliche Überwachung',
    hardware: 'GPU',
  },
  {
    title: 'Transfer Pricing',
    description: 'Kommende Modul für proaktive Compliance in internationalen Steuerstrategien.',
    components: 'Steueragent',
    hardware: 'CPU/GPU',
  },
  {
    title: 'Pillar 2 & ESG Reporting',
    description: 'Skalierbare Warnungen für globale Steuerstandards und Nachhaltigkeitsberichterstattung.',
    components: 'Dashboard',
    hardware: 'GPU',
  },
  {
    title: 'Arbeitsrecht, DSGVO, Vertragsrecht',
    description: 'Erweiterbar auf andere Rechtsbereiche mit Dokumentenparsing und Kommunikationsprofilen.',
    components: 'Multimodal',
    hardware: 'CPU/GPU',
  },
];

// Main Hero Component (now only informational content)
export default function Hero() {
  return (
    <>
      <title>Juris-Diction(AI)ry | KI-gestützte Rechtsüberwachung</title>
      <meta
        name="description"
        content="Entdecken Sie Juris-Diction(AI)ry, angetrieben von dwani.ai – eine GenAI-Plattform für proaktive Rechtsüberwachung im Steuerrecht und darüber hinaus. Von E-Rechnungen bis ESG sorgen Sie mit sicheren, multimodalen Analysen für Compliance."
      />
      <meta
        name="keywords"
        content="Juris-Diction(AI)ry, dwani.ai, Rechtsüberwachung, Steuer-Compliance, E-Rechnungen, Transfer Pricing, Pillar 2, ESG Reporting, KI-Rechtswarnungen"
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
              Angetrieben von dwani.ai
            </Typography>

            <Divider sx={{ width: '60%', mx: 'auto', my: 2 }} />

            <Typography
              variant="body1"
              sx={{ textAlign: 'center', color: 'text.secondary' }}
            >
              Proaktive Rechtsüberwachung: Von der Krise zum strategischen Vorteil
            </Typography>

            <Divider sx={{ width: '60%', mx: 'auto', my: 2 }} />

            <Typography
              variant="body1"
              sx={{ textAlign: 'center', color: 'text.secondary' }}
            >
              Vom Konzept zu Live-Warnungen in 24 Stunden. Erkunden Sie das{' '}
              <Link
                href="https://tax.dwani.ai/dashboard"
                target="_blank"
                color="primary"
                aria-label="dwani.ai uberTax Dashboard"
              >
                Dashboard
              </Link>.
            </Typography>

            <Button
              variant="contained"
              color="primary"
              href="https://dev-tax.dwani.ai"
              target="_blank"
              size="large"
              sx={{ mt: 2, px: 4, py: 1.5, borderRadius: 2 }}
              aria-label="Try Multimodal Inference for Legal Docs"
            >
              Ausprobieren - KI-Workflow
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
                Rechtsüberwachung ist ein kritischer Schmerzpunkt
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
                Die doppelte Vorteilslösung
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
              Skalierbare Module & Workflow
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
              Kontaktieren Sie uns
            </Typography>
            <Typography
              variant="body1"
              sx={{ textAlign: 'center', color: 'text.secondary' }}
            >
              Werden Sie Mitglied in unserer{' '}
              <Link
                href="https://discord.gg/9Fq8J9Gnz3"
                target="_blank"
                color="primary"
                aria-label="Join dwani.ai Discord community"
              >
                Discord-Community
              </Link>{' '}
              für Kooperationen.
              <br />
              Haben Sie Fragen?{' '}
              <Link
                href="https://calendar.app.google/j1L2Sh6sExfWpUTZ7"
                target="_blank"
                color="primary"
                aria-label="Schedule a demo with dwani.ai"
              >
                Termin vereinbaren
              </Link>.
            </Typography>
          </Stack>
        </Container>
      </Box>
    </>
  );
}