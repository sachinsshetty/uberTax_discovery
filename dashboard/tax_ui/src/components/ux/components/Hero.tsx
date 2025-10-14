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
import UserApp from '../../User/UserApp';

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


<UserApp/>
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