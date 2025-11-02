import React from 'react';
import {
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Box,
  Typography,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { CountryProfileData } from './CountryProfileData';

const CountryProfile: React.FC<{ data: CountryProfileData | null }> = ({ data }) => {
  if (!data) {
    return (
      <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
        <CardContent>
          <Alert severity="warning">No country data selected.</Alert>
        </CardContent>
      </Card>
    );
  }

  // Helper function to safely access nested properties with fallback
  function safeGet<T>(obj: any, path: string, fallback: T): T {
    const result = path.split('.').reduce((current: any, key: string) => {
      return current && current[key] !== undefined ? current[key] : fallback;
    }, obj);
    return result ?? fallback;
  }

  // Adapt labels for English countries if needed, but for simplicity, keep German structure where applicable
  //const isGerman = data.country.includes('Kroatien');
  // ... rest remains the same, but add conditional labels if desired
  // For now, assume data fields are used directly, user can adjust

  // Helper to handle array joining safely
  const safeJoin = (value: any): string => {
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    return value || 'N/A';
  };

  return (
    <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a', maxHeight: 800, overflow: 'auto' }}>
      <CardContent sx={{ '& .MuiAccordionSummary-root': { backgroundColor: '#1e2d4a', borderColor: '#2a3b5a' } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" fontWeight="600" sx={{ color: 'grey.400' }}>
            Country Profile: {data.country}
          </Typography>
          {/* Optional: Add a refresh or export button here if needed */}
        </Box>
        
        {/* General Data - Always expanded for quick overview */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'cyan.400' }}>General Data</Typography>
          <List dense>
            <ListItem>
              <ListItemText primary="Mandate Status" secondary={data.mandateStatus || 'N/A'} />
            </ListItem>
            <ListItem>
              <ListItemText primary="Archiving Period (Years)" secondary={safeGet(data, 'archivingPeriod', 'N/A')} />
            </ListItem>
          </List>
        </Box>

        {/* Scope */}
        <Accordion defaultExpanded={false} sx={{ mb: 2, '&:before': { display: 'none' } }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'grey.300' }} />}>
            <Typography variant="h6" sx={{ color: 'cyan.400', flexGrow: 1 }}>Scope</Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Box sx={{ ml: 2, p: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Triggers</Typography>
              <List dense>
                <ListItem><ListItemText primary="Residents" secondary={safeGet(data.scope, 'triggers.residents', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Non-Residents with VAT ID" secondary={safeGet(data.scope, 'triggers.nonResidentsWithVatId', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Logic" secondary={safeGet(data.scope, 'triggers.logic', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>B2B</Typography>
              <List dense>
                <ListItem><ListItemText primary="Status" secondary={safeGet(data.scope, 'b2b.status', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Start Date" secondary={safeGet(data.scope, 'b2b.startDate', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Staggered Introduction" secondary={safeGet(data.scope, 'b2b.staggered.applies', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Threshold" secondary={safeGet(data.scope, 'b2b.staggered.threshold', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>B2G</Typography>
              <List dense>
                <ListItem><ListItemText primary="Status" secondary={safeGet(data.scope, 'b2g.status', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Start Date" secondary={safeGet(data.scope, 'b2g.startDate', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Staggered Introduction" secondary={safeGet(data.scope, 'b2g.staggered.applies', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>B2C</Typography>
              <List dense>
                <ListItem><ListItemText primary="Reporting Obligation" secondary={safeGet(data.scope, 'b2c.reportingObligation', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Start Date" secondary={safeGet(data.scope, 'b2c.startDate', 'N/A')} /></ListItem>
              </List>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Architecture */}
        <Accordion defaultExpanded={false} sx={{ mb: 2, '&:before': { display: 'none' } }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'grey.300' }} />}>
            <Typography variant="h6" sx={{ color: 'cyan.400', flexGrow: 1 }}>Architecture</Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Box sx={{ ml: 2, p: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Model</Typography>
              <List dense>
                <ListItem><ListItemText primary="Type" secondary={safeGet(data, 'architecture.model.type', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Corner Model" secondary={safeGet(data, 'architecture.model.cornerModel', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Description" secondary={safeGet(data, 'architecture.model.description', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Formats</Typography>
              <List dense>
                <ListItem><ListItemText primary="EN16931" secondary={safeGet(data, 'architecture.formats.en16931.status', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="National CIUS" secondary={safeGet(data, 'architecture.formats.nationalCius.schemaName', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Allowed Syntaxes" secondary={safeJoin(safeGet(data, 'architecture.formats.allowedSyntaxes', []))} /></ListItem>
                <ListItem><ListItemText primary="PDF Conform" secondary={safeGet(data, 'architecture.formats.pdfConform', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Transmission</Typography>
              <List dense>
                <ListItem><ListItemText primary="PEPPOL" secondary={safeGet(data, 'architecture.transmission.peppol.status', 'N/A')} /></ListItem>
              </List>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Reporting */}
        <Accordion defaultExpanded={false} sx={{ mb: 2, '&:before': { display: 'none' } }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'grey.300' }} />}>
            <Typography variant="h6" sx={{ color: 'cyan.400', flexGrow: 1 }}>Reporting Obligations</Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Box sx={{ ml: 2, p: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>State Platform</Typography>
              <List dense>
                <ListItem><ListItemText primary="Applies" secondary={safeGet(data, 'reporting.statePlatform.applies', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Name" secondary={safeGet(data, 'reporting.statePlatform.name', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Mandatory" secondary={safeGet(data, 'reporting.statePlatform.mandatory', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Clearance</Typography>
              <List dense>
                <ListItem><ListItemText primary="Real-time CTC" secondary={safeGet(data, 'reporting.clearance.realTimeCtc', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Validity After Release" secondary={safeGet(data, 'reporting.clearance.validityAfterRelease', 'N/A')} /></ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Reporting Requirements</Typography>
              <List dense>
                <ListItem><ListItemText primary="DRR" secondary={safeGet(data, 'reporting.reportingReq.drr', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Real-time" secondary={safeGet(data, 'reporting.reportingReq.realTime', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Frequency" secondary={safeGet(data, 'reporting.reportingReq.frequency', 'N/A')} /></ListItem>
              </List>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Additional */}
        <Accordion defaultExpanded={false} sx={{ mb: 2, '&:before': { display: 'none' } }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'grey.300' }} />}>
            <Typography variant="h6" sx={{ color: 'cyan.400', flexGrow: 1 }}>Additional Requirements</Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Box sx={{ ml: 2, p: 2 }}>
              <List dense>
                <ListItem><ListItemText primary="System Certification" secondary={safeGet(data, 'additional.systemCert', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="SAFT Obligation" secondary={safeGet(data, 'additional.saft.obligation', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Local IDs Obligation" secondary={safeGet(data, 'additional.localIds.obligation', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Transaction Status Reporting" secondary={safeGet(data, 'additional.transactionStatusReporting', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Special Notes" secondary={safeGet(data, 'additional.specialNotes', 'N/A')} /></ListItem>
                <ListItem><ListItemText primary="Sanctions" secondary={safeGet(data, 'additional.sanctions', 'N/A')} /></ListItem>
              </List>
            </Box>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

export default CountryProfile;